from enum import Enum


class AbilityName(Enum):

    """
    Represents a player ability
    """

    NULL_SPELL_SPECIAL_CASE = 0
    ANCESTOR_IDENTITY_ABILITY = 1
    ANCESTOR_LIFE_ABILITY = 2
    ANIMATE_DEAD_ABILITY = 3
    ANIMATE_REMAINS_ABILITY = 4
    APOCALYPSE_ABILITY = 5
    BANISH_ABILITY = 6
    BANISH_SELF_ABILITY = 7
    BEND_SPACE_ABILITY = 9
    BEND_TIME_ABILITY = 10
    BERSERK_ABILITY = 11
    BLINK_ABILITY = 12
    BRAND_WEAPON_WITH_HOLY_ABILITY = 13
    BRAND_WEAPON_WITH_PAIN_ABILITY = 14
    BRIAR_PATCH_ABILITY = 15
    BRIBE_BRANCH_ABILITY = 16
    BROTHERS_IN_ARMS_ABILITY = 17
    CALL_MERCHANT_ABILITY = 18
    CHANNEL_MAGIC_ABILITY = 19
    CLEANSING_FLAME_ABILITY = 20
    CONTROLLED_BLINK_ABILITY = 21
    CORRUPT_ABILITY = 22
    CORRUPT_WEAPON_ABILITY = 23
    CURE_BAD_MUTATIONS_ABILITY = 24
    CURSE_ITEM_ABILITY = 25
    DEAL_FOUR_ABILITY = 26
    DEPART_ABYSS_ABILITY = 27
    DISASTER_AREA_ABILITY = 28
    DIVINE_PROTECTION_ABILITY = 29
    DIVINE_SHIELD_ABILITY = 30
    DIVINE_VIGOUR_ABILITY = 31
    DRAIN_LIFE_ABILITY = 32
    DRAW_OUT_POWER_ABILITY = 33
    ELEMENTAL_FORCE_ABILITY = 34
    ENSLAVE_SOUL_ABILITY = 35
    EXSANGUINATE_ABILITY = 8
    FINESSE_ABILITY = 36
    FLIGHT_ABILITY = 37
    FORGET_SPELL_ABILITY = 38
    GAIN_RANDOM_MUTATIONS_ABILITY = 39
    GIVE_ITEM_TO_FOLLOWER_ABILITY = 40
    GRAND_FINALE_ABILITY = 41
    GREATER_HEALING_ABILITY = 42
    GROW_BALLISTOMYCETE_ABILITY = 43
    GROW_OKLOB_PLANT_ABILITY = 44
    HEAL_OTHER_ABILITY = 45
    HEAL_WOUNDS_ABILITY = 46
    HEAVENLY_STORM_ABILITY = 47
    HEROISM_ABILITY = 48
    HOP_ABILITY = 49
    IDEALISE_ABILITY = 50
    IMPRISON_ABILITY = 51
    LESSER_HEALING_ABILITY = 52
    LINE_PASS_ABILITY = 53
    MAJOR_DESTRUCTION_ABILITY = 54
    MINOR_DESTRUCTION_ABILITY = 55
    OVERGROW_ABILITY = 56
    PICK_A_CARD_ANY_CARD_ABILITY = 57
    POTION_PETITION_ABILITY = 58
    POWER_LEAP_ABILITY = 59
    PURIFICATION_ABILITY = 60
    RECALL_ABILITY = 61
    RECALL_UNDEAD_SLAVES_ABILITY = 62
    RECEIVE_CORPSES_ABILITY = 63
    RECEIVE_NECRONOMICON_ABILITY = 64
    RECITE_ABILITY = 65
    REQUEST_JELLY_ABILITY = 66
    RESURRECTION_ABILITY = 67
    REVIVIFY_ABILITY = 95
    ROLLING_CHARGE_ABILITY = 68
    SANCTUARY_ABILITY = 69
    SCRYING_ABILITY = 70
    SERPENTS_LASH_ABILITY = 71
    SHADOW_FORM_ABILITY = 72
    SHADOW_STEP_ABILITY = 73
    SLIMIFY_ABILITY = 74
    SLOUCH_ABILITY = 75
    SMITE_ABILITY = 76
    SPIT_POISON_ABILITY = 77
    STACK_FIVE_ABILITY = 78
    STEP_FROM_TIME_ABILITY = 79
    STOMP_ABILITY = 80
    SUMMON_DIVINE_WARRIOR_ABILITY = 81
    SUMMON_GREATER_SERVANT_ABILITY = 82
    SUMMON_LESSER_SERVANT_ABILITY = 83
    TEMPORAL_DISTORTION_ABILITY = 84
    TOGGLE_DIVINE_ENERGY_ABILITY = 85
    TOGGLE_INJURY_MIRROR_ABILITY = 86
    TORMENT_ABILITY = 87
    TRANSFER_KNOWLEDGE_ABILITY = 88
    TRANSFERENCE_ABILITY = 89
    TRIPLE_DRAW_ABILITY = 90
    TROGS_HAND_ABILITY = 91
    UPHEAVAL_ABILITY = 92
    VITALISATION_ABILITY = 93
    WALL_JUMP_ABILITY = 94
    RENOUNCE_RELIGION_ABILITY = 95


class AbilityNameMapping:

    """
    Assists parsing what ability the player has from websocket data

    # TODO add more here as they are discovered - crawl wiki unreliable
    """

    ability_menu_messages_lookup = {

        "Exsanguinate": AbilityName.EXSANGUINATE_ABILITY,
        "Revivify": AbilityName.REVIVIFY_ABILITY,

    }


class Ability:

    """
    Represent a spell that a player can or has learned.
    """

    NULL_ABILITY_VECTOR = [AbilityName.NULL_SPELL_SPECIAL_CASE, -1, -1, -1, False, False]

    # Data describing the length of the ability name for the first word in the ability name
    # This is used for parsing abilities from raw JSON in autobahn game connection class
    # A better solution would be to use Regex
    ABILITY_NAME_LENGTH = {'Berserk':1,
                           'Renounce':2}

    def __init__(self, abilityname: AbilityName, fail_chance: int, mp_cost: bool, piety_cost: bool, delay_cost: bool, frailty_cost: bool):
        self.abilityname = abilityname
        self.fail_chance = fail_chance
        self.mp_cost = mp_cost
        self.piety_cost = piety_cost
        self.delay_cost = delay_cost
        self.frailty_cost = frailty_cost

    def get_ability_vector(self):
        return [self.abilityname, self.fail_chance, int(self.mp_cost), int(self.piety_cost), int(self.delay_cost), int(self.frailty_cost)]

    def get_ability_pddl(self):
        # TODO
        pass

    def __hash__(self):
        return hash("{}{}".format(self.abilityname, self.fail_chance))

    def __eq__(self, other):
        return self.abilityname == other.abilityname and self.fail_chance == other.fail_chance
