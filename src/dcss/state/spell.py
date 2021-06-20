from dcss.state.spellname import SpellName
from dcss.state.skill import Skill


class Spell:

    """
    Represent a spell that a player can or has learned.
    """

    def __init__(self, spellname: SpellName, skills: [Skill], fail_chance: int, level: int):
        self.spellname = spellname
        self.skills = skills
        self.fail_chance = fail_chance
        self.level = level

    def get_spell_vector(self):
        # TODO
        pass

    def get_spell_pddl(self):
        # TODO
        pass

