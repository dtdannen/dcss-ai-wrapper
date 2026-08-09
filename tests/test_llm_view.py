"""
Offline tests for dcss.agent.llm_view - no Docker, no webtiles server, no network.

Run with:  python tests/test_llm_view.py

Plain asserts in a script rather than pytest, matching the rest of tests/ and
the fact that pytest is not in requirements.txt.

The GameStates here are built by hand: attributes set directly, cells pushed
through CellMap.add_or_update_cell, and messages/inventory fed through the same
GameState.process_* methods the connection layer calls, so the shapes match what
the server actually produces without needing a server.

Covers the four things Phase 1 is defined by:
  1. normal play renders without raising
  2. a fresh GameState (no map data at all) renders without raising
  3. an item that never went through equip() renders without raising
  4. observe() neither mutates the state nor varies between calls
plus a state that raises on every attribute access, since "never raises" is the
property that actually protects the connection thread.
"""

import enum
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from dcss.agent.llm_view import MESSAGE_TURNS, observe, render
from dcss.state.game import GameState
from dcss.state.inventoryitem import InventoryItem
from dcss.state.statuseffect import StatusEffect

REQUIRED_KEYS = ('status', 'effects', 'map', 'messages', 'inventory', 'legend',
                 'suggested_actions', 'alive')


# --- state fixtures ---------------------------------------------------------

# A small room: wall border, floor inside, the player, a rat, a potion and the
# down staircase. Coordinates are deliberately negative-to-positive because the
# cell map is centred on wherever the agent started.
ROOM = [
    '#######',
    '#..!..#',
    '#..@..#',
    '#.r...#',
    '#....>#',
    '#######',
]


def make_playing_state():
    gs = GameState()

    gs.player_name = 'Testo'
    gs.player_title = 'the Cutpurse'
    gs.player_species = 'Minotaur'
    gs.player_current_hp = 12
    gs.player_hp_max = 31
    gs.player_current_mp = 2
    gs.player_mp_max = 5
    gs.player_ac = 3
    gs.player_ev = 11
    gs.player_sh = 0
    gs.player_strength = 18
    gs.player_int = 8
    gs.player_dex = 12
    gs.player_level = 4
    gs.player_gold = 27
    gs.player_place = 'Dungeon'
    gs.player_depth = 3
    gs.game_turn = 812
    gs.game_time = 8120
    gs.player_status_effects = {StatusEffect.POISON_STATUS_EFFECT,
                                StatusEffect.SLOW_STATUS_EFFECT}

    gs.cellmap.set_current_place('Dungeon')
    gs.cellmap.set_current_depth(3)
    for row, line in enumerate(ROOM):
        for col, glyph in enumerate(line):
            x, y = col - 3, row - 2
            gs.cellmap.add_or_update_cell(x, y, {'x': x, 'y': y, 'g': glyph})

    # Same path the connection layer uses: HTML in, stripped text out.
    gs.process_messages([
        {'turn': 811, 'text': '<span class="fg7">You hit the rat.</span>'},
        {'turn': 812, 'text': '<span class="fg7">The rat bites you!</span>'},
        {'turn': 812, 'text': 'You feel sick.'},
    ])

    gs.process_inv({
        '0': {'name': '+0 short sword', 'quantity': 1, 'base_type': 0},
        '3': {'name': '2 potions of curing', 'quantity': 2, 'base_type': 7},
    })
    gs.process_equip({'0': 0})  # weapon slot holds inventory item 0

    return gs


def make_state_with_never_equipped_item():
    """
    InventoryItem.__init__ never assigns self.equipped, so is_item_equipped()
    raises AttributeError on anything that did not go through equip(). Building
    the item directly (rather than via process_inv, whose tail equips or
    unequips everything) reproduces that exactly.
    """
    gs = GameState()
    gs.player_current_hp = 20
    gs.player_hp_max = 20
    gs.inventory_by_id['5'] = InventoryItem('5', 'a scroll of fear', 1, 5)
    return gs


class ExplodingState:
    """Every attribute access raises. Nothing in the LLM path may propagate."""

    def __getattr__(self, name):
        raise RuntimeError('exploding state: {}'.format(name))


# --- purity helper ----------------------------------------------------------

def snapshot(obj, depth=0):
    """
    Recursive value-repr of an object graph, used to detect mutation. Compares
    contents rather than identity, so an in-place list append or a flag being
    reset shows up as a difference.
    """
    if depth > 6:
        return '...'
    if isinstance(obj, (str, int, float, bool, type(None))):
        return repr(obj)
    if isinstance(obj, enum.Enum) or isinstance(obj, type):
        return repr(obj)
    if isinstance(obj, (list, tuple)):
        return '[{}]'.format(','.join(snapshot(o, depth + 1) for o in obj))
    if isinstance(obj, (set, frozenset)):
        return '{{{}}}'.format(','.join(sorted(snapshot(o, depth + 1) for o in obj)))
    if isinstance(obj, dict):
        return '{{{}}}'.format(','.join(
            '{}:{}'.format(snapshot(k, depth + 1), snapshot(v, depth + 1))
            for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))))
    if hasattr(obj, '__dict__'):
        return '{}({})'.format(type(obj).__name__, snapshot(vars(obj), depth + 1))
    return repr(obj)


# --- tests ------------------------------------------------------------------

def test_normal_play_observes_and_renders():
    gs = make_playing_state()
    obs = observe(gs)

    for key in REQUIRED_KEYS:
        assert key in obs, 'observation is missing key {!r}'.format(key)
    assert 'error' not in obs, 'observation reported an error: {}'.format(obs.get('error'))
    assert obs['alive'] is True

    status = obs['status']
    assert status['hp'] == 12 and status['hp_max'] == 31
    assert status['hp_fraction'] is not None and 0.38 < status['hp_fraction'] < 0.39
    assert status['turn'] == 812
    assert status['place'] == 'Dungeon' and status['depth'] == 3
    # Position must come from the cell map, not the legacy map_obj coordinates,
    # which stay None even here.
    assert gs.get_player_xy() == (None, None), 'legacy accessor unexpectedly populated'
    assert (status['x'], status['y']) == (0, 0)

    assert obs['effects'] == ['poison', 'slow'], obs['effects']

    map_section = obs['map']
    assert map_section['available'] is True
    assert map_section['explored_cells'] == len(ROOM) * len(ROOM[0])
    assert '@' in map_section['ascii']
    assert '>' in map_section['ascii'] and '#' in map_section['ascii']
    assert map_section['bounds']['min_x'] == -3 and map_section['bounds']['max_y'] == 3

    # Legend covers exactly what is on the floor, plus the unexplored marker.
    legend = obs['legend']
    for glyph in ('@', '#', '.', '>', '!', 'r', ' '):
        assert glyph in legend, 'legend is missing {!r}: {}'.format(glyph, legend)
    assert legend['r'] == 'monster'
    assert '<' not in legend, 'legend lists a glyph that is not on the map'

    messages = obs['messages']
    assert [m['turn'] for m in messages] == [811, 812]
    assert messages[0]['lines'] == ['You hit the rat.']
    assert messages[1]['lines'] == ['The rat bites you!', 'You feel sick.']
    assert '<span' not in render(obs), 'HTML leaked into the prompt text'

    inventory = obs['inventory']
    assert [i['letter'] for i in inventory] == ['a', 'd'], inventory
    assert inventory[0]['equipped'] is True
    assert inventory[1]['equipped'] is False and inventory[1]['quantity'] == 2

    # A monster is visible, so attacking is promoted to the front.
    assert obs['suggested_actions'][0]['command'] == 'AUTO_FIGHT'

    text = render(obs)
    assert isinstance(text, str) and len(text) > 200
    for expected in ('turn 812', 'HP 12/31', 'MAP', 'LEGEND', 'RECENT MESSAGES',
                     'INVENTORY', 'SUGGESTED ACTIONS', 'short sword', 'The rat bites you!'):
        assert expected in text, 'render() dropped {!r}'.format(expected)
    assert 'render failed' not in text


def test_fresh_state_observes_and_renders():
    """
    The case that breaks the naive version: on a fresh GameState the cell map has
    no bounds and no place/depth entry, and draw_cell_map() raises if called.
    """
    gs = GameState()
    obs = observe(gs)

    for key in REQUIRED_KEYS:
        assert key in obs
    assert 'error' not in obs
    assert obs['map']['available'] is False
    assert obs['map']['ascii'] == ''
    assert obs['map']['explored_cells'] == 0
    assert obs['legend'] == {}
    assert obs['messages'] == [] and obs['inventory'] == []
    assert obs['status']['hp'] is None
    assert obs['alive'] is True
    assert obs['suggested_actions'], 'suggestions should not depend on map data'

    # Confirms the workaround is load-bearing rather than defensive decoration.
    raised = False
    try:
        gs.get_cell_map().draw_cell_map()
    except Exception:
        raised = True
    assert raised, 'draw_cell_map() no longer raises on a fresh state - review the guard'

    text = render(obs)
    assert isinstance(text, str) and 'no map data yet' in text
    assert 'HP ?/?' in text
    assert 'render failed' not in text


def test_never_equipped_item_observes_and_renders():
    gs = make_state_with_never_equipped_item()
    item = gs.inventory_by_id['5']

    assert not hasattr(item, 'equipped'), \
        'InventoryItem now sets .equipped - the getattr workaround can be revisited'
    raised = False
    try:
        item.is_item_equipped()
    except AttributeError:
        raised = True
    assert raised, 'is_item_equipped() no longer raises - review the workaround'

    obs = observe(gs)
    assert 'error' not in obs
    assert len(obs['inventory']) == 1
    entry = obs['inventory'][0]
    assert entry['equipped'] is False
    assert entry['name'] == 'a scroll of fear'
    assert entry['letter'] == 'f'

    text = render(obs)
    assert 'a scroll of fear' in text and 'render failed' not in text


def test_observe_is_pure_and_deterministic():
    gs = make_playing_state()

    before = snapshot(gs)
    first = observe(gs)
    after_first = snapshot(gs)
    assert before == after_first, 'observe() mutated the GameState'

    second = observe(gs)
    assert first == second, 'observe() is not deterministic across calls'
    assert snapshot(gs) == before, 'observe() mutated the GameState on the second call'
    assert render(first) == render(second), 'render() is not deterministic'

    # The flag-resetting accessors are the specific mutation risk: they clear
    # what they report, so calling one from observe() would silently eat an event.
    gs.cannot_move = True
    gs.too_terrified_to_move = True
    gs.just_gained_level = True
    observe(gs)
    assert gs.cannot_move and gs.too_terrified_to_move and gs.just_gained_level, \
        'observe() called a flag-resetting accessor'


def test_dead_state_is_reported():
    gs = make_playing_state()
    gs.process_messages([{'turn': 813, 'text': 'You die...'}])
    obs = observe(gs)
    assert obs['alive'] is False
    assert 'YOU ARE DEAD' in render(obs)

    # Zero HP counts as dead even if the death message never arrived.
    other = make_playing_state()
    other.player_current_hp = 0
    assert observe(other)['alive'] is False


def test_low_hp_promotes_resting_when_nothing_is_visible():
    gs = GameState()
    gs.player_current_hp = 3
    gs.player_hp_max = 30
    assert observe(gs)['suggested_actions'][0]['command'] == 'REST_AND_LONG_WAIT'


def test_messages_are_capped_to_the_last_turns():
    gs = GameState()
    gs.process_messages([{'turn': t, 'text': 'message {}'.format(t)} for t in range(1, 41)])
    messages = observe(gs)['messages']
    assert len(messages) == MESSAGE_TURNS
    assert [m['turn'] for m in messages] == list(range(41 - MESSAGE_TURNS, 41))


def test_nothing_raises_on_hostile_input():
    """The property that protects the connection thread, tested directly."""
    obs = observe(ExplodingState())
    assert isinstance(obs, dict)
    for key in REQUIRED_KEYS:
        assert key in obs
    assert isinstance(render(obs), str)

    for bad in (None, {}, [], 'not a dict', {'status': None, 'map': None},
                {'status': {'hp': 'lots'}, 'inventory': [None], 'messages': [None],
                 'suggested_actions': [None], 'legend': None}):
        text = render(bad)
        assert isinstance(text, str), 'render({!r}) returned {!r}'.format(bad, type(text))
        assert 'render failed' not in text, 'render({!r}) hit its last-resort handler'.format(bad)

    assert isinstance(observe(None), dict)
    assert isinstance(observe(object()), dict)


TESTS = [
    test_normal_play_observes_and_renders,
    test_fresh_state_observes_and_renders,
    test_never_equipped_item_observes_and_renders,
    test_observe_is_pure_and_deterministic,
    test_dead_state_is_reported,
    test_low_hp_promotes_resting_when_nothing_is_visible,
    test_messages_are_capped_to_the_last_turns,
    test_nothing_raises_on_hostile_input,
]


def main():
    failures = 0
    for test in TESTS:
        try:
            test()
        except Exception as e:
            failures += 1
            print('FAIL  {}: {}: {}'.format(test.__name__, type(e).__name__, e))
        else:
            print('ok    {}'.format(test.__name__))

    print('\n{}/{} passed'.format(len(TESTS) - failures, len(TESTS)))
    if failures == 0:
        print('\n--- sample rendered observation ---')
        print(render(observe(make_playing_state())))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
