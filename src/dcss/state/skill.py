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
        "Unarmed Combat": SkillName.UNARMED_COMBAT,
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
        "Transmutation": SkillName.TRANSMUTATION,
        "Fire": SkillName.FIRE_MAGIC,
        "Ice": SkillName.ICE_MAGIC,
        "Air": SkillName.AIR_MAGIC,
        "Earth": SkillName.EARTH_MAGIC,
        "Poison": SkillName.POISON_MAGIC,
        "Invocations": SkillName.INVOCATIONS,
        "Evocations": SkillName.EVOCATIONS,
        "Stealth": SkillName.STEALTH}

    skill_name_to_pddl_obj = {
        SkillName.FIGHTING:"fighting",
        SkillName.LONG_BLADES:"long_blades",
        SkillName.SHORT_BLADES:"short_blades",
        SkillName.AXES:"axes",
        SkillName.MACES_FLAILS:"maces_&_flails",
        SkillName.POLEARMS:"polearms",
        SkillName.STAVES:"staves",
        SkillName.UNARMED_COMBAT:"unarmed_combat",
        SkillName.BOWS:"bows",
        SkillName.CROSSBOWS:"crossbows",
        SkillName.THROWING:"throwing",
        SkillName.SLINGS:"slings",
        SkillName.ARMOUR:"armour",
        SkillName.DODGING:"dodging",
        SkillName.SHIELDS:"shields",
        SkillName.SPELLCASTING:"spellcasting",
        SkillName.CONJURATIONS:"conjurations",
        SkillName.HEXES:"hexes",
        SkillName.CHARMS:"charms",
        SkillName.SUMMONINGS:"summonings",
        SkillName.NECROMANCY:"necromancy",
        SkillName.TRANSLOCATIONS:"translocations",
        SkillName.TRANSMUTATION:"transmutation",
        SkillName.FIRE_MAGIC:"fire_magic",
        SkillName.ICE_MAGIC:"ice_magic",
        SkillName.AIR_MAGIC:"air_magic",
        SkillName.EARTH_MAGIC:"earth_magic",
        SkillName.POISON_MAGIC:"poison_magic",
        SkillName.INVOCATIONS:"invocations",
        SkillName.EVOCATIONS:"evocations",
        SkillName.STEALTH:"stealth"}


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
        """
            Returns predicates about this skill consisting of:

                (training_off ?skill - skill)
                (training_low ?skill - skill)
                (training_high ?skill - skill)
                (player_skill_level ?skill - skill ?amount - qualitative_quantity)
        """
        print("Generating PDDL for Skill {}".format(self.skillname.name))
        print("   Level is {}".format(self.level))
        print("   % Training is {}".format(self.percent_training))
        print("   Aptitude is {}".format(self.percent_training))
        pddl_skill_facts = []
        if self.percent_training and self.percent_training > 0:
            if self.percent_training >= 50:
                pddl_skill_facts.append("(training_high {})".format(SkillMapping.skill_name_to_pddl_obj[self.skillname]))
            elif 0 < self.percent_training < 50:
                pddl_skill_facts.append("(training_low {})".format(SkillMapping.skill_name_to_pddl_obj[self.skillname]))
        else:
            pddl_skill_facts.append("(training_off {})".format(SkillMapping.skill_name_to_pddl_obj[self.skillname]))

        quantitative_choices = ['low', 'medium_low', 'medium', 'medium_high', 'high', 'maxed']

        skill_level_index = 0
        if self.level > 0:
            max_skill_level = 27  # from the game
            skill_level_index = int((self.level / max_skill_level) * len(quantitative_choices))
            pddl_skill_facts.append("(player_skill_level {} {})".format(SkillMapping.skill_name_to_pddl_obj[self.skillname], quantitative_choices[skill_level_index]))
        else:
            pddl_skill_facts.append("(player_skill_level {} {})".format(SkillMapping.skill_name_to_pddl_obj[self.skillname],
                                                                    'none'))

        return pddl_skill_facts





































