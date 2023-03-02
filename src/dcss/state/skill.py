from enum import Enum
from dcss.actions.menuchoice import MenuChoice


class SkillName(Enum):

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

        "Fighting": SkillName.FIGHTING,
        "Long Blades": SkillName.LONG_BLADES,
        "Short Blades": SkillName.SHORT_BLADES,
        "Axes": SkillName.AXES,
        "Maces & Flails": SkillName.MACES_FLAILS,
        "Polearms": SkillName.POLEARMS,
        "Staves": SkillName.STAVES,
        "Unarmed Combat*": SkillName.UNARMED_COMBAT,
        "Bows": SkillName.BOWS,
        "Crossbows": SkillName.CROSSBOWS,
        "Throwing": SkillName.THROWING,
        "Slings": SkillName.SLINGS,
        "Armour": SkillName.ARMOUR,
        "Dodging": SkillName.DODGING,
        "Shields": SkillName.SHIELDS,
        "Spellcasting": SkillName.SPELLCASTING,
        "Conjurations": SkillName.CONJURATIONS,
        "Hexes": SkillName.HEXES,
        "Charms": SkillName.CHARMS,
        "Summonings": SkillName.SUMMONINGS,
        "Necromancy": SkillName.NECROMANCY,
        "Translocations": SkillName.TRANSLOCATIONS,
        "Transmutations": SkillName.TRANSMUTATION,
        "Fire Magic": SkillName.FIRE_MAGIC,
        "Ice Magic": SkillName.ICE_MAGIC,
        "Air Magic": SkillName.AIR_MAGIC,
        "Earth Magic": SkillName.EARTH_MAGIC,
        "Poison Magic": SkillName.POISON_MAGIC,
        "Invocations": SkillName.INVOCATIONS,
        "Evocations": SkillName.EVOCATIONS,
        "Stealth": SkillName.STEALTH}


class Skill:
    """
    Represents a skill of a player, including its current level and whether the player is training it (and by how much).
    """

    NULL_SKILL_VECTOR = [SkillName.NULL_SKILL_SPECIAL_CASE, MenuChoice.NONE, -1.0, -1, None]

    def __init__(self, skillname: SkillName, menuchoice: MenuChoice, level: float, percent_currently_training: int, aptitude: int):
        self.skillname = skillname
        self.menuchoice = menuchoice
        self.level = level
        self.percent_training = percent_currently_training
        self.aptitude = aptitude

    def get_skill_vector(self):
        return [self.skillname, self.level, self.percent_training, self.aptitude]

    def get_skill_pddl(self):
        # TODO
        pass




































