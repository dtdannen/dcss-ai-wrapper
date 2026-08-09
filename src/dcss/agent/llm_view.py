"""
Prompt-facing view of a DCSS ``GameState``.

``observe(gs)`` turns the wrapper's state object into plain, JSON-friendly data;
``render(obs)`` turns that data into the text a language model actually reads.
The split exists so the same observation can be fed to a model, logged, or
diffed across turns without re-deriving it.

Two properties are load-bearing and are asserted by ``tests/test_llm_view.py``:

*Neither function may raise.* ``get_action()`` runs inside the asyncio loop, so
an exception here does not merely produce a bad prompt - it stalls the
connection thread for the rest of the episode. Every field is therefore read
defensively and every section is built inside its own guard, so a failure in one
part of the state (a half-parsed item, a map that has not arrived yet) costs
that section only.

*``observe()`` is pure.* It never mutates ``gs`` and returns the same dict for
the same state, which means the flag-resetting accessors on ``GameState``
(``agent_cannot_move``, ``is_agent_too_terrified``, ``agent_just_leveled_up``,
all of which clear the flag they report) must not be called from here; the
underlying attributes are read directly instead. Sets are sorted on the way out
so repeated calls compare equal.

Known wrapper bugs are worked around, not fixed - the state files are shared
with the RL track:

* ``InventoryItem.__init__`` never assigns ``self.equipped``, so
  ``is_item_equipped()`` raises on any item that never went through ``equip()``.
  Read it with ``getattr(item, 'equipped', False)``.
* ``CellMap.draw_cell_map()`` indexes ``min_x``/``max_x`` and the place/depth
  dict unguarded, so it raises on a fresh game. Call it only once map data is
  confirmed present.
* ``GameState.get_player_xy()`` returns legacy ``map_obj`` coordinates that stay
  ``None``. The authoritative position is ``cellmap.agent_x``/``agent_y``, which
  is also what agrees with the ``@`` on the rendered map.
* ``GameState.draw_cell_map()`` prints and returns ``None``; the string comes
  from ``gs.get_cell_map().draw_cell_map()``.

The map section deliberately shows the *whole explored floor* rather than a
window around the player - that memory of where the agent has already been is
the structural advantage this view has over the radius-3 RL observation.
"""

from dcss.actions.command import Command

# How many distinct game turns of messages to carry. Messages arrive keyed by
# turn with several lines per turn, so this is turns, not lines.
MESSAGE_TURNS = 10

# Glyph meanings, transcribed from the branches in dcss/state/cell.py. Anything
# alphabetic that is not a plant is a monster; monster names/distances are
# deliberately deferred, so monsters appear as map glyphs only for now.
GLYPH_MEANINGS = {
    '@': 'you (the player)',
    '#': 'wall',
    '.': 'floor',
    '>': 'staircase down',
    '<': 'staircase up',
    '+': 'closed door',
    "'": 'open door',
    '8': 'statue',
    '⌠': 'fountain',
    '≈': 'lava',
    '☘': 'tree',
    '♣': 'tree',
    '†': 'corpse',
    '§': 'smoke',
    '°': 'magical condensation cloud',
    '○': 'magical condensation cloud',
    '☼': 'flame cloud',
    '^': 'trap or shaft',
    '!': 'potion on floor',
    '?': 'scroll on floor',
    '(': 'ammunition on floor',
    ')': 'weapon on floor',
    '[': 'armour on floor',
    '=': 'ring on floor',
    '"': 'amulet on floor',
    ':': 'book on floor',
    '/': 'wand on floor',
    '\\': 'staff on floor',
    '}': 'miscellaneous item on floor',
    '$': 'gold',
    '0': 'the Orb of Zot',
    'p': 'plant',
    'P': 'plant',
    ';': 'monster',
}

UNEXPLORED_GLYPH = ' '
UNEXPLORED_MEANING = 'unexplored (not yet seen)'

# Actions worth offering every turn. Names are checked against the Command enum
# at call time so a rename in command.py drops the entry rather than handing the
# model a command that cannot be executed. North is y-1: draw_cell_map() walks
# rows from min_y down to max_y, so smaller y is higher on the map.
BASE_SUGGESTIONS = (
    ('AUTO_EXPLORE', 'walk toward the nearest unexplored area (good default when nothing threatens)'),
    ('AUTO_FIGHT', 'attack the nearest visible monster'),
    ('REST_AND_LONG_WAIT', 'rest until HP/MP recover or something interrupts'),
    ('WAIT_1_TURN', 'stand still for a single turn'),
    ('MOVE_OR_ATTACK_N', 'move or attack north (y-1, up on the map)'),
    ('MOVE_OR_ATTACK_S', 'move or attack south (y+1, down on the map)'),
    ('MOVE_OR_ATTACK_E', 'move or attack east (x+1, right on the map)'),
    ('MOVE_OR_ATTACK_W', 'move or attack west (x-1, left on the map)'),
    ('MOVE_OR_ATTACK_NE', 'move or attack north-east'),
    ('MOVE_OR_ATTACK_NW', 'move or attack north-west'),
    ('MOVE_OR_ATTACK_SE', 'move or attack south-east'),
    ('MOVE_OR_ATTACK_SW', 'move or attack south-west'),
    ('OPEN_DOOR', "open an adjacent door ('+' on the map)"),
    ('TRAVEL_STAIRCASE_DOWN', "travel to the nearest known down staircase ('>')"),
    ('TRAVEL_STAIRCASE_UP', "travel to the nearest known up staircase ('<')"),
    ('PICKUP_ITEM', 'pick up whatever is on the tile you are standing on'),
)

# Below this fraction of max HP, resting is promoted ahead of exploring.
LOW_HP_FRACTION = 0.4


# --- internal helpers -------------------------------------------------------
# Every one of these swallows exceptions by design; see the module docstring.

def _attr(obj, name, default=None):
    """getattr that also survives a property raising on access."""
    try:
        value = getattr(obj, name)
    except Exception:
        return default
    return default if value is None else value


def _call(fn, default=None):
    try:
        value = fn()
    except Exception:
        return default
    return default if value is None else value


def _enum_name(value):
    """'POISON_STATUS_EFFECT' (enum or string) -> 'poison'."""
    try:
        name = getattr(value, 'name', None) or str(value)
        for suffix in ('_STATUS_EFFECT', '_MUTATION'):
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        return name.lower().replace('_', ' ')
    except Exception:
        return 'unknown'


def _turn_sort_key(turn):
    """Turn keys come off the wire and are usually ints, but not guaranteed;
    sorting a mixed dict would raise, so ints sort first and the rest by text."""
    try:
        return (0, int(turn), '')
    except Exception:
        return (1, 0, str(turn))


def _is_monster_glyph(glyph):
    try:
        return bool(glyph) and len(glyph) == 1 and (
            glyph == ';' or (glyph.isalpha() and glyph not in ('p', 'P')))
    except Exception:
        return False


def _get_cellmap(gs):
    cellmap = _call(lambda: gs.get_cell_map())
    if cellmap is None:
        cellmap = _attr(gs, 'cellmap')
    return cellmap


def _get_current_cells(cellmap):
    """The {(x, y): Cell} dict for the floor the player is on, or {}."""
    try:
        by_place = cellmap.place_depth_to_x_y_to_cells
        cells = by_place.get(cellmap.current_place, {}).get(cellmap.current_depth)
        return cells if isinstance(cells, dict) else {}
    except Exception:
        return {}


def _bounds_known(cellmap):
    try:
        return None not in (cellmap.min_x, cellmap.max_x, cellmap.min_y, cellmap.max_y)
    except Exception:
        return False


# --- observation sections ---------------------------------------------------

def _status(gs, cellmap):
    hp = _attr(gs, 'player_current_hp')
    hp_max = _attr(gs, 'player_hp_max')
    hp_fraction = None
    try:
        if hp is not None and hp_max:
            hp_fraction = round(float(hp) / float(hp_max), 3)
    except Exception:
        hp_fraction = None

    return {
        'name': _attr(gs, 'player_name', ''),
        'species': _attr(gs, 'player_species', ''),
        'title': _attr(gs, 'player_title', ''),
        'xl': _attr(gs, 'player_level'),
        'xp_progress': _attr(gs, 'player_progress'),
        'hp': hp,
        'hp_max': hp_max,
        'hp_fraction': hp_fraction,
        'mp': _attr(gs, 'player_current_mp'),
        'mp_max': _attr(gs, 'player_mp_max'),
        'ac': _attr(gs, 'player_ac'),
        'ev': _attr(gs, 'player_ev'),
        'sh': _attr(gs, 'player_sh'),
        'strength': _attr(gs, 'player_strength'),
        'intelligence': _attr(gs, 'player_int'),
        'dexterity': _attr(gs, 'player_dex'),
        'gold': _attr(gs, 'player_gold'),
        'god': _attr(gs, 'player_god'),
        'piety_rank': _attr(gs, 'player_piety_rank'),
        'place': _attr(gs, 'player_place', ''),
        'depth': _attr(gs, 'player_depth'),
        'turn': _attr(gs, 'game_turn'),
        'time': _attr(gs, 'game_time'),
        # Legacy get_player_xy() stays (None, None) even with a full cell map;
        # the cell map's own coordinates are the ones the '@' agrees with.
        'x': _attr(cellmap, 'agent_x'),
        'y': _attr(cellmap, 'agent_y'),
    }


def _effects(gs):
    """Sorted for determinism - the underlying container is a set."""
    try:
        effects = _attr(gs, 'player_status_effects', set())
        return sorted({_enum_name(e) for e in effects})
    except Exception:
        return []


def _map(gs, cellmap):
    section = {
        'available': False,
        'ascii': '',
        'place': _attr(cellmap, 'current_place', ''),
        'depth': _attr(cellmap, 'current_depth'),
        'player_x': _attr(cellmap, 'agent_x'),
        'player_y': _attr(cellmap, 'agent_y'),
        'explored_cells': 0,
        'bounds': None,
        'note': 'no map data yet',
    }
    if cellmap is None:
        return section

    cells = _get_current_cells(cellmap)
    section['explored_cells'] = len(cells)

    # draw_cell_map() indexes min_x/max_x and the place/depth dict without
    # guarding, so both have to be confirmed present before it is safe to call.
    if not cells or not _bounds_known(cellmap):
        return section

    section['bounds'] = {
        'min_x': _attr(cellmap, 'min_x'),
        'max_x': _attr(cellmap, 'max_x'),
        'min_y': _attr(cellmap, 'min_y'),
        'max_y': _attr(cellmap, 'max_y'),
    }

    drawn = _call(lambda: cellmap.draw_cell_map())
    if not isinstance(drawn, str):
        section['note'] = 'map could not be drawn'
        return section

    # Trailing spaces are pure token cost; the leading y-label keeps rows aligned.
    section['ascii'] = '\n'.join(line.rstrip() for line in drawn.split('\n')).rstrip('\n')
    section['available'] = True
    section['note'] = ''
    return section


def _legend(cellmap):
    """Only the glyphs actually on this floor, so the legend stays short and honest."""
    legend = {}
    try:
        for cell in _get_current_cells(cellmap).values():
            glyph = _attr(cell, 'g')
            if not isinstance(glyph, str) or not glyph:
                continue
            if glyph in GLYPH_MEANINGS:
                legend[glyph] = GLYPH_MEANINGS[glyph]
            elif _is_monster_glyph(glyph):
                legend[glyph] = 'monster'
            else:
                legend[glyph] = 'unrecognised glyph'
    except Exception:
        pass
    if legend:
        legend[UNEXPLORED_GLYPH] = UNEXPLORED_MEANING
    return {glyph: legend[glyph] for glyph in sorted(legend)}


def _messages(gs):
    try:
        messages = _attr(gs, 'messages', {})
        if not isinstance(messages, dict):
            return []
        recent = sorted(messages.keys(), key=_turn_sort_key)[-MESSAGE_TURNS:]
        out = []
        for turn in recent:
            lines = messages.get(turn) or []
            if isinstance(lines, str):
                lines = [lines]
            texts = [str(line).strip() for line in lines if str(line).strip()]
            if texts:
                out.append({'turn': turn, 'lines': texts})
        return out
    except Exception:
        return []


def _inventory(gs):
    items = []
    try:
        by_id = _attr(gs, 'inventory_by_id', {})
        if not isinstance(by_id, dict):
            return items
        for key in sorted(by_id.keys(), key=_turn_sort_key):
            item = by_id.get(key)
            if item is None:
                continue
            items.append({
                # get_letter() indexes a fixed alphabet, so a large id would raise.
                'letter': _call(lambda i=item: i.get_letter(), '?'),
                'name': _attr(item, 'name', ''),
                'quantity': _attr(item, 'quantity'),
                'type': _enum_name(_attr(item, 'item_type', '')) or '',
                # is_item_equipped() raises on any item never passed to equip().
                'equipped': bool(getattr(item, 'equipped', False)),
                'bonus': _attr(item, 'item_bonus', 0),
                'cursed': bool(_attr(item, 'cursed', False)),
            })
    except Exception:
        pass
    return items


def _suggested_actions(monsters_visible, hp_fraction):
    entries = []
    for name, why in BASE_SUGGESTIONS:
        if hasattr(Command, name):
            entries.append({'command': name, 'why': why})

    low_hp = hp_fraction is not None and hp_fraction < LOW_HP_FRACTION

    def rank(entry):
        if monsters_visible and entry['command'] == 'AUTO_FIGHT':
            return 0
        if not monsters_visible and low_hp and entry['command'] == 'REST_AND_LONG_WAIT':
            return 0
        return 1

    entries.sort(key=rank)  # stable, so the base order survives underneath
    return entries


# --- public API -------------------------------------------------------------

def observe(gs):
    """
    Structured snapshot of ``gs`` for an LLM. Pure: never mutates ``gs``, and
    two calls on an unchanged state return equal dicts. Never raises - on
    catastrophic failure it returns a skeleton with an ``error`` key rather than
    propagating, because an exception here stalls the connection thread.

    Keys: ``alive``, ``status``, ``effects``, ``map``, ``legend``, ``messages``,
    ``inventory``, ``suggested_actions``.
    """
    try:
        cellmap = _get_cellmap(gs)
        status = _status(gs, cellmap)
        map_section = _map(gs, cellmap)

        monsters_visible = False
        try:
            monsters_visible = any(
                _is_monster_glyph(_attr(cell, 'g'))
                for cell in _get_current_cells(cellmap).values())
        except Exception:
            monsters_visible = False

        died = bool(_attr(gs, 'died', False))
        hp = status.get('hp')
        alive = not died and not (hp is not None and hp <= 0)

        return {
            'alive': alive,
            'status': status,
            'effects': _effects(gs),
            'map': map_section,
            'legend': _legend(cellmap),
            'messages': _messages(gs),
            'inventory': _inventory(gs),
            'suggested_actions': _suggested_actions(monsters_visible, status.get('hp_fraction')),
        }
    except Exception as e:
        return {
            'alive': True,
            'status': {},
            'effects': [],
            'map': {'available': False, 'ascii': '', 'note': 'observation failed'},
            'legend': {},
            'messages': [],
            'inventory': [],
            'suggested_actions': [],
            'error': '{}: {}'.format(type(e).__name__, e),
        }


def _fmt(value, missing='?'):
    if value is None or value == '':
        return missing
    if isinstance(value, float):
        return '{:g}'.format(value)
    return str(value)


def _render_header(status, alive, lines):
    turn = _fmt(status.get('turn'))
    lines.append('=== DCSS - turn {} ==='.format(turn))

    who = ' '.join(p for p in (status.get('name'), status.get('title')) if p)
    species = status.get('species')
    if species:
        who = '{} ({})'.format(who, species) if who else str(species)
    if who:
        lines.append(who)

    hp_part = 'HP {}/{}'.format(_fmt(status.get('hp')), _fmt(status.get('hp_max')))
    fraction = status.get('hp_fraction')
    if isinstance(fraction, (int, float)):
        hp_part += ' ({}%)'.format(int(round(fraction * 100)))
    lines.append('{}   MP {}/{}   AC {}  EV {}  SH {}'.format(
        hp_part, _fmt(status.get('mp')), _fmt(status.get('mp_max')),
        _fmt(status.get('ac')), _fmt(status.get('ev')), _fmt(status.get('sh'))))
    lines.append('Str {}  Int {}  Dex {}   XL {}   Gold {}'.format(
        _fmt(status.get('strength')), _fmt(status.get('intelligence')),
        _fmt(status.get('dexterity')), _fmt(status.get('xl')), _fmt(status.get('gold'))))

    place = _fmt(status.get('place'), 'unknown')
    depth = status.get('depth')
    if depth is not None:
        place = '{}:{}'.format(place, depth)
    lines.append('Place {}   Position ({}, {})   God {}'.format(
        place, _fmt(status.get('x')), _fmt(status.get('y')),
        _fmt(status.get('god'), 'none')))

    if not alive:
        lines.append('YOU ARE DEAD - the episode is over.')


def render(obs):
    """
    Prompt-ready text for the dict from ``observe()``. Pure and never raises;
    a partial or empty dict renders as far as it can rather than failing.
    """
    try:
        if not isinstance(obs, dict):
            return '(no observation available)'

        status = obs.get('status') or {}
        lines = []
        _render_header(status, obs.get('alive', True), lines)

        effects = obs.get('effects') or []
        lines.append('Status effects: {}'.format(', '.join(effects) if effects else 'none'))

        map_section = obs.get('map') or {}
        lines.append('')
        lines.append("MAP - whole explored floor, '{}' = {}".format(
            UNEXPLORED_GLYPH, UNEXPLORED_MEANING))
        if map_section.get('available') and map_section.get('ascii'):
            lines.append('({} tiles seen on this floor; rows are labelled with y, '
                         'smaller y is north)'.format(map_section.get('explored_cells', 0)))
            lines.append(map_section['ascii'])
        else:
            lines.append('({})'.format(_fmt(map_section.get('note'), 'no map data yet')))

        legend = obs.get('legend') or {}
        if legend:
            lines.append('')
            lines.append('LEGEND')
            for glyph, meaning in legend.items():
                shown = "' '" if glyph == UNEXPLORED_GLYPH else glyph
                lines.append('  {}  {}'.format(shown, meaning))

        lines.append('')
        lines.append('RECENT MESSAGES (last {} turns)'.format(MESSAGE_TURNS))
        messages = obs.get('messages') or []
        if messages:
            for entry in messages:
                turn = _fmt((entry or {}).get('turn'))
                for text in (entry or {}).get('lines') or []:
                    lines.append('  [turn {}] {}'.format(turn, text))
        else:
            lines.append('  (none)')

        lines.append('')
        lines.append('INVENTORY')
        inventory = obs.get('inventory') or []
        if inventory:
            for item in inventory:
                item = item or {}
                extras = []
                quantity = item.get('quantity')
                if isinstance(quantity, int) and quantity > 1:
                    extras.append('x{}'.format(quantity))
                if item.get('type'):
                    extras.append(str(item['type']))
                if item.get('equipped'):
                    extras.append('equipped')
                if item.get('cursed'):
                    extras.append('cursed')
                suffix = ' [{}]'.format(', '.join(extras)) if extras else ''
                lines.append('  {} - {}{}'.format(
                    _fmt(item.get('letter')), _fmt(item.get('name'), '(unknown item)'), suffix))
        else:
            lines.append('  (empty)')

        lines.append('')
        lines.append('SUGGESTED ACTIONS (any Command enum member is valid, these are just the common ones)')
        for entry in obs.get('suggested_actions') or []:
            entry = entry or {}
            lines.append('  {} - {}'.format(_fmt(entry.get('command')), _fmt(entry.get('why'), '')))

        if obs.get('error'):
            lines.append('')
            lines.append('NOTE: the observation was incomplete ({})'.format(obs['error']))

        return '\n'.join(lines)
    except Exception as e:
        return '(render failed: {}: {})'.format(type(e).__name__, e)
