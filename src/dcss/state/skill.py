from enum import Enum


class Skill(Enum):

    """
    Represents a skill
    """

    NULL_SKILL_SPECIAL_CASE = 0

    FIGHTING = 1
    LONG_BLADES = 2
    SHORT_BLADES = 3
    AXES = 4
    MACES_FLAILS = 5
    POLEARMS = 6
    STAVES = 7
    UNARMED_COMBAT = 8
    BOWS = 9
    CROSSBOWS = 10
    THROWING = 11
    SLINGS = 12
    ARMOUR = 13
    DODGING = 14
    SHIELDS = 15
    SPELLCASTING = 16
    CONJURATIONS = 17
    HEXES = 18
    CHARMS = 19
    SUMMONINGS = 20
    NECROMANCY = 21
    TRANSLOCATIONS = 22
    TRANSMUTATION = 23
    FIRE_MAGIC = 24
    ICE_MAGIC = 25
    AIR_MAGIC = 26
    EARTH_MAGIC = 27
    POISON_MAGIC = 28
    INVOCATIONS = 29
    EVOCATIONS = 30
    STEALTH = 31


class SkillMapping:

    """
    Assists parsing what skill the player has from websocket data
    """

    skill_game_text_lookup = {

        "Fighting": Skill.FIGHTING,
        "Long Blades": Skill.LONG_BLADES,
        "Short Blades": Skill.SHORT_BLADES,
        "Axes": Skill.AXES,
        "Maces & Flails": Skill.MACES_FLAILS,
        "Polearms": Skill.POLEARMS,
        "Staves": Skill.STAVES,
        "Unarmed Combat*": Skill.UNARMED_COMBAT,
        "Bows": Skill.BOWS,
        "Crossbows": Skill.CROSSBOWS,
        "Throwing": Skill.THROWING,
        "Slings": Skill.SLINGS,
        "Armour": Skill.ARMOUR,
        "Dodging": Skill.DODGING,
        "Shields": Skill.SHIELDS,
        "Spellcasting": Skill.SPELLCASTING,
        "Conjurations": Skill.CONJURATIONS,
        "Hexes": Skill.HEXES,
        "Charms": Skill.CHARMS,
        "Summonings": Skill.SUMMONINGS,
        "Necromancy": Skill.NECROMANCY,
        "Translocations": Skill.TRANSLOCATIONS,
        "Transmutation": Skill.TRANSMUTATION,
        "Fire": Skill.FIRE_MAGIC,
        "Ice": Skill.ICE_MAGIC,
        "Air": Skill.AIR_MAGIC,
        "Earth": Skill.EARTH_MAGIC,
        "Poison": Skill.POISON_MAGIC,
        "Invocations": Skill.INVOCATIONS,
        "Evocations": Skill.EVOCATIONS,
        "Stealth": Skill.STEALTH}









































