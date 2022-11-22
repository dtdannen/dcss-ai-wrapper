from enum import Enum


class StatusEffect(Enum):

    """
    Represents a status effect, including abilities
    """

    AGILE_STATUS_EFFECT = 1
    ALIVE_STATUS_EFFECT = 91
    ANTIMAGIC_STATUS_EFFECT = 2
    AUGMENTATION_STATUS_EFFECT = 3
    BAD_FORMS_STATUS_EFFECT = 4
    BERSERK_STATUS_EFFECT = 5
    BLACK_MARK_STATUS_EFFECT = 6
    BLIND_STATUS_EFFECT = 7
    BLOODLESS_STATUS_EFFECT = 92
    BRILLIANT_STATUS_EFFECT = 8
    CHARM_STATUS_EFFECT = 9
    CONFUSING_TOUCH_STATUS_EFFECT = 10
    CONFUSION_STATUS_EFFECT = 11
    CONSTRICTION_STATUS_EFFECT = 12
    COOLDOWNS_STATUS_EFFECT = 13
    CORONA_STATUS_EFFECT = 14
    CORROSION_STATUS_EFFECT = 15
    DARKNESS_STATUS_EFFECT = 16
    DAZED_STATUS_EFFECT = 17
    DEATH_CHANNEL_STATUS_EFFECT = 18
    DEATHS_DOOR_STATUS_EFFECT = 19
    DEFLECT_MISSILES_STATUS_EFFECT = 20
    DISJUNCTION_STATUS_EFFECT = 21
    DIVINE_PROTECTION_STATUS_EFFECT = 22
    DIVINE_SHIELD_STATUS_EFFECT = 23
    DOOM_HOWL_STATUS_EFFECT = 24
    DRAIN_STATUS_EFFECT = 25
    ENGORGED_STATUS_EFFECT = 26
    ENGULF_STATUS_EFFECT = 27
    FAST_SLOW_STATUS_EFFECT = 28
    FEAR_STATUS_EFFECT = 29
    FINESSE_STATUS_EFFECT = 30
    FIRE_VULNERABLE_STATUS_EFFECT = 31
    FLAYED_STATUS_EFFECT = 32
    FLIGHT_STATUS_EFFECT = 33
    FROZEN_STATUS_EFFECT = 34
    HASTE_STATUS_EFFECT = 35
    HEAVENLY_STORM_STATUS_EFFECT = 36
    HELD_STATUS_EFFECT = 37
    HEROISM_STATUS_EFFECT = 38
    HORRIFIED_STATUS_EFFECT = 39
    INNER_FLAME_STATUS_EFFECT = 40
    INVISIBILITY_STATUS_EFFECT = 41
    LAVA_STATUS_EFFECT = 42
    LEDAS_LIQUEFACTION_STATUS_EFFECT = 43
    MAGIC_CONTAMINATION_STATUS_EFFECT = 45
    MARK_STATUS_EFFECT = 46
    MESMERISED_STATUS_EFFECT = 47
    MIGHT_STATUS_EFFECT = 48
    MIRROR_DAMAGE_STATUS_EFFECT = 49
    NO_POTIONS_STATUS_EFFECT = 50
    NO_SCROLLS_STATUS_EFFECT = 51
    OLGREBS_TOXIC_RADIANCE_STATUS_EFFECT = 52
    ORB_STATUS_EFFECT = 53
    OZOCUBUS_ARMOUR_STATUS_EFFECT = 54
    PARALYSIS_STATUS_EFFECT = 55
    PETRIFYING_STATUS_EFFECT = 56
    PETRIFIED_STATUS_EFFECT = 91
    POISON_STATUS_EFFECT = 57
    POWERED_BY_DEATH_STATUS_EFFECT = 58
    QUAD_DAMAGE_STATUS_EFFECT = 59
    RECALL_STATUS_EFFECT = 60
    REGENERATING_STATUS_EFFECT = 61
    REPEL_MISSILES_STATUS_EFFECT = 62
    RESISTANCE_STATUS_EFFECT = 63
    RING_OF_FLAMES_STATUS_EFFECT = 64
    SAPPED_MAGIC_STATUS_EFFECT = 65
    SCRYING_STATUS_EFFECT = 66
    SEARING_RAY_STATUS_EFFECT = 67
    SERPENTS_LASH_STATUS_EFFECT = 68
    SHROUD_OF_GOLUBRIA_STATUS_EFFECT = 69
    SICKNESS_STATUS_EFFECT = 70
    SILENCE_STATUS_EFFECT = 71
    SLEEP_STATUS_EFFECT = 73
    SLIMIFY_STATUS_EFFECT = 74
    SLOW_STATUS_EFFECT = 75
    SLUGGISH_STATUS_EFFECT = 76
    STARVING_STATUS_EFFECT = 77
    STAT_ZERO_STATUS_EFFECT = 78
    STICKY_FLAME_STATUS_EFFECT = 79
    STILL_WINDS_STATUS_EFFECT = 80
    SWIFTNESS_STATUS_EFFECT = 81
    TELEPORT_PREVENTION_STATUS_EFFECT = 82
    TELEPORT_STATUS_EFFECT = 83
    TORNADO_STATUS_EFFECT = 84
    TRANSMUTATIONS_STATUS_EFFECT = 85
    UMBRA_STATUS_EFFECT = 86
    VITALISATION_STATUS_EFFECT = 87
    VULNERABLE_STATUS_EFFECT = 88
    WATER_STATUS_EFFECT = 89
    WEAK_STATUS_EFFECT = 90
    ZOT_STATUS_EFFECT = 91


class StatusEffectMapping:

    """
    Assists parsing what status effect the player has from websocket data
    """

    status_effect_menu_messages_lookup = {

    "You are agile": StatusEffect.AGILE_STATUS_EFFECT,
    "": StatusEffect.ANTIMAGIC_STATUS_EFFECT,
    "": StatusEffect.AUGMENTATION_STATUS_EFFECT,
    "": StatusEffect.BAD_FORMS_STATUS_EFFECT,
    "": StatusEffect.BERSERK_STATUS_EFFECT,
    "": StatusEffect.BLACK_MARK_STATUS_EFFECT,
    "": StatusEffect.BLIND_STATUS_EFFECT,
    "": StatusEffect.BRILLIANT_STATUS_EFFECT,
    "": StatusEffect.CHARM_STATUS_EFFECT,
    "": StatusEffect.CONFUSING_TOUCH_STATUS_EFFECT,
    "": StatusEffect.CONFUSION_STATUS_EFFECT,
    "": StatusEffect.CONSTRICTION_STATUS_EFFECT,
    "": StatusEffect.COOLDOWNS_STATUS_EFFECT,
    "": StatusEffect.CORONA_STATUS_EFFECT,
    "": StatusEffect.CORROSION_STATUS_EFFECT,
    "": StatusEffect.DARKNESS_STATUS_EFFECT,
    "": StatusEffect.DAZED_STATUS_EFFECT,
    "": StatusEffect.DEATH_CHANNEL_STATUS_EFFECT,
    "": StatusEffect.DEATHS_DOOR_STATUS_EFFECT,
    "": StatusEffect.DEFLECT_MISSILES_STATUS_EFFECT,
    "": StatusEffect.DISJUNCTION_STATUS_EFFECT,
    "": StatusEffect.DIVINE_PROTECTION_STATUS_EFFECT,
    "": StatusEffect.DIVINE_SHIELD_STATUS_EFFECT,
    "": StatusEffect.DOOM_HOWL_STATUS_EFFECT,
    "": StatusEffect.DRAIN_STATUS_EFFECT,
    "": StatusEffect.ENGORGED_STATUS_EFFECT,
    "": StatusEffect.ENGULF_STATUS_EFFECT,
    "": StatusEffect.FAST_SLOW_STATUS_EFFECT,
    "": StatusEffect.FEAR_STATUS_EFFECT,
    "": StatusEffect.FINESSE_STATUS_EFFECT,
    "": StatusEffect.FIRE_VULNERABLE_STATUS_EFFECT,
    "": StatusEffect.FLAYED_STATUS_EFFECT,
    "": StatusEffect.FLIGHT_STATUS_EFFECT,
    "": StatusEffect.FROZEN_STATUS_EFFECT,
    "": StatusEffect.HASTE_STATUS_EFFECT,
    "": StatusEffect.HEAVENLY_STORM_STATUS_EFFECT,
    "": StatusEffect.HELD_STATUS_EFFECT,
    "": StatusEffect.HEROISM_STATUS_EFFECT,
    "": StatusEffect.HORRIFIED_STATUS_EFFECT,
    "": StatusEffect.INNER_FLAME_STATUS_EFFECT,
    "": StatusEffect.INVISIBILITY_STATUS_EFFECT,
    "": StatusEffect.LAVA_STATUS_EFFECT,
    "": StatusEffect.LEDAS_LIQUEFACTION_STATUS_EFFECT,
    "": StatusEffect.MAGIC_CONTAMINATION_STATUS_EFFECT,
    "": StatusEffect.MARK_STATUS_EFFECT,
    "": StatusEffect.MESMERISED_STATUS_EFFECT,
    "": StatusEffect.MIGHT_STATUS_EFFECT,
    "": StatusEffect.MIRROR_DAMAGE_STATUS_EFFECT,
    "": StatusEffect.NO_POTIONS_STATUS_EFFECT,
    "": StatusEffect.NO_SCROLLS_STATUS_EFFECT,
    "": StatusEffect.OLGREBS_TOXIC_RADIANCE_STATUS_EFFECT,
    "": StatusEffect.ORB_STATUS_EFFECT,
    "": StatusEffect.OZOCUBUS_ARMOUR_STATUS_EFFECT,
    "": StatusEffect.PARALYSIS_STATUS_EFFECT,
    "": StatusEffect.PETRIFYING_STATUS_EFFECT,
    "": StatusEffect.PETRIFIED_STATUS_EFFECT,
    "": StatusEffect.POISON_STATUS_EFFECT,
    "": StatusEffect.POWERED_BY_DEATH_STATUS_EFFECT,
    "": StatusEffect.QUAD_DAMAGE_STATUS_EFFECT,
    "": StatusEffect.RECALL_STATUS_EFFECT,
    "": StatusEffect.REGENERATING_STATUS_EFFECT,
    "": StatusEffect.REPEL_MISSILES_STATUS_EFFECT,
    "": StatusEffect.RESISTANCE_STATUS_EFFECT,
    "": StatusEffect.RING_OF_FLAMES_STATUS_EFFECT,
    "": StatusEffect.SAPPED_MAGIC_STATUS_EFFECT,
    "": StatusEffect.SCRYING_STATUS_EFFECT,
    "": StatusEffect.SEARING_RAY_STATUS_EFFECT,
    "": StatusEffect.SERPENTS_LASH_STATUS_EFFECT,
    "": StatusEffect.SHROUD_OF_GOLUBRIA_STATUS_EFFECT,
    "": StatusEffect.SICKNESS_STATUS_EFFECT,
    "": StatusEffect.SILENCE_STATUS_EFFECT,
    "": StatusEffect.SLEEP_STATUS_EFFECT,
    "": StatusEffect.SLIMIFY_STATUS_EFFECT,
    "": StatusEffect.SLOW_STATUS_EFFECT,
    "": StatusEffect.SLUGGISH_STATUS_EFFECT,
    "": StatusEffect.STARVING_STATUS_EFFECT,
    "": StatusEffect.STAT_ZERO_STATUS_EFFECT,
    "": StatusEffect.STICKY_FLAME_STATUS_EFFECT,
    "": StatusEffect.STILL_WINDS_STATUS_EFFECT,
    "": StatusEffect.SWIFTNESS_STATUS_EFFECT,
    "": StatusEffect.TELEPORT_PREVENTION_STATUS_EFFECT,
    "": StatusEffect.TELEPORT_STATUS_EFFECT,
    "": StatusEffect.TORNADO_STATUS_EFFECT,
    "": StatusEffect.TRANSMUTATIONS_STATUS_EFFECT,
    "": StatusEffect.UMBRA_STATUS_EFFECT,
    "": StatusEffect.VITALISATION_STATUS_EFFECT,
    "": StatusEffect.VULNERABLE_STATUS_EFFECT,
    "": StatusEffect.WATER_STATUS_EFFECT,
    "": StatusEffect.WEAK_STATUS_EFFECT,

    }


class StatusEffectPDDLMapping:
    """
    Assists writing pddl what status effect the player has
    """

    status_effect_pddl_lookup = {

        StatusEffect.AGILE_STATUS_EFFECT: 'agile_status',
        StatusEffect.ANTIMAGIC_STATUS_EFFECT: 'antimagic_status',
        StatusEffect.AUGMENTATION_STATUS_EFFECT: 'augmentation_status',
        StatusEffect.BAD_FORMS_STATUS_EFFECT: 'bad_forms_status',
        StatusEffect.BERSERK_STATUS_EFFECT: 'berserk_status',
        StatusEffect.BLACK_MARK_STATUS_EFFECT: 'black_mark_status',
        StatusEffect.BLIND_STATUS_EFFECT: 'blind_status',
        StatusEffect.BRILLIANT_STATUS_EFFECT: 'brilliant_status',
        StatusEffect.CHARM_STATUS_EFFECT: 'charm_status',
        StatusEffect.CONFUSING_TOUCH_STATUS_EFFECT: 'confusing_touch_status',
        StatusEffect.CONFUSION_STATUS_EFFECT: 'confusion_status',
        StatusEffect.CONSTRICTION_STATUS_EFFECT: 'constriction_status',
        StatusEffect.COOLDOWNS_STATUS_EFFECT: 'cooldowns_status',
        StatusEffect.CORONA_STATUS_EFFECT: 'corona_status',
        StatusEffect.CORROSION_STATUS_EFFECT: 'corrosion_status',
        StatusEffect.DARKNESS_STATUS_EFFECT: 'darkness_status',
        StatusEffect.DAZED_STATUS_EFFECT: 'dazed_status',
        StatusEffect.DEATH_CHANNEL_STATUS_EFFECT: 'death_channel_status',
        StatusEffect.DEATHS_DOOR_STATUS_EFFECT: 'deaths_door_status',
        StatusEffect.DEFLECT_MISSILES_STATUS_EFFECT: 'deflect_missiles_status',
        StatusEffect.DISJUNCTION_STATUS_EFFECT: 'disjunction_status',
        StatusEffect.DIVINE_PROTECTION_STATUS_EFFECT: 'divine_protection_status',
        StatusEffect.DIVINE_SHIELD_STATUS_EFFECT: 'divine_shield_status',
        StatusEffect.DOOM_HOWL_STATUS_EFFECT: 'doom_howl_status',
        StatusEffect.DRAIN_STATUS_EFFECT: 'drain_status',
        StatusEffect.ENGORGED_STATUS_EFFECT: 'engorged_status',
        StatusEffect.ENGULF_STATUS_EFFECT: 'engulf_status',
        StatusEffect.FAST_SLOW_STATUS_EFFECT: 'fast_slow_status',
        StatusEffect.FEAR_STATUS_EFFECT: 'fear_status',
        StatusEffect.FINESSE_STATUS_EFFECT: 'finesse_status',
        StatusEffect.FIRE_VULNERABLE_STATUS_EFFECT: 'fire_vulnerable_status',
        StatusEffect.FLAYED_STATUS_EFFECT: 'flayed_status',
        StatusEffect.FLIGHT_STATUS_EFFECT: 'flight_status',
        StatusEffect.FROZEN_STATUS_EFFECT: 'frozen_status',
        StatusEffect.HASTE_STATUS_EFFECT: 'haste_status',
        StatusEffect.HEAVENLY_STORM_STATUS_EFFECT: 'heavenly_storm_status',
        StatusEffect.HELD_STATUS_EFFECT: 'held_status',
        StatusEffect.HEROISM_STATUS_EFFECT: 'heroism_status',
        StatusEffect.HORRIFIED_STATUS_EFFECT: 'horrified_status',
        StatusEffect.INNER_FLAME_STATUS_EFFECT: 'inner_flame_status',
        StatusEffect.INVISIBILITY_STATUS_EFFECT: 'invisibility_status',
        StatusEffect.LAVA_STATUS_EFFECT: 'in_lava_status',
        StatusEffect.LEDAS_LIQUEFACTION_STATUS_EFFECT: 'ledas_liquefaction_status',
        StatusEffect.MAGIC_CONTAMINATION_STATUS_EFFECT: 'magic_contamination_status',
        StatusEffect.MARK_STATUS_EFFECT: 'mark_status',
        StatusEffect.MESMERISED_STATUS_EFFECT: 'mesmerised_status',
        StatusEffect.MIGHT_STATUS_EFFECT: 'might_status',
        StatusEffect.MIRROR_DAMAGE_STATUS_EFFECT: 'mirror_damage_status',
        StatusEffect.NO_POTIONS_STATUS_EFFECT: 'no_potions_status',
        StatusEffect.NO_SCROLLS_STATUS_EFFECT: 'no_scrolls_status',
        StatusEffect.OLGREBS_TOXIC_RADIANCE_STATUS_EFFECT: 'olgrebs_toxic_radiance_status',
        StatusEffect.ORB_STATUS_EFFECT: 'orb_status',
        StatusEffect.OZOCUBUS_ARMOUR_STATUS_EFFECT: 'ozocubus_armour_status',
        StatusEffect.PARALYSIS_STATUS_EFFECT: 'paralysis_status',
        StatusEffect.PETRIFYING_STATUS_EFFECT: 'petrifying_status',
        StatusEffect.PETRIFIED_STATUS_EFFECT: 'petrified_status',
        StatusEffect.POISON_STATUS_EFFECT: 'poison_status',
        StatusEffect.POWERED_BY_DEATH_STATUS_EFFECT: 'powered_by_death_status',
        StatusEffect.QUAD_DAMAGE_STATUS_EFFECT: 'quad_damage_status',
        StatusEffect.RECALL_STATUS_EFFECT: 'recall_status',
        StatusEffect.REGENERATING_STATUS_EFFECT: 'regenerating_status',
        StatusEffect.REPEL_MISSILES_STATUS_EFFECT: 'repel_missiles_status',
        StatusEffect.RESISTANCE_STATUS_EFFECT: 'resistance_status_effect_status',
        StatusEffect.RING_OF_FLAMES_STATUS_EFFECT: 'ring_of_flames_status',
        StatusEffect.SAPPED_MAGIC_STATUS_EFFECT: 'sapped_magic_status',
        StatusEffect.SCRYING_STATUS_EFFECT: 'scrying_status',
        StatusEffect.SEARING_RAY_STATUS_EFFECT: 'searing_ray_status',
        StatusEffect.SERPENTS_LASH_STATUS_EFFECT: 'serpents_lash_status',
        StatusEffect.SHROUD_OF_GOLUBRIA_STATUS_EFFECT: 'shroud_of_golubria_status',
        StatusEffect.SICKNESS_STATUS_EFFECT: 'sickness_status',
        StatusEffect.SILENCE_STATUS_EFFECT: 'silence_status',
        StatusEffect.SLEEP_STATUS_EFFECT: 'sleep_status',
        StatusEffect.SLIMIFY_STATUS_EFFECT: 'slimify_status',
        StatusEffect.SLOW_STATUS_EFFECT: 'slow_status',
        StatusEffect.SLUGGISH_STATUS_EFFECT: 'sluggish_status',
        StatusEffect.STARVING_STATUS_EFFECT: 'starving_status',
        StatusEffect.STAT_ZERO_STATUS_EFFECT: 'stat_zero_status',
        StatusEffect.STICKY_FLAME_STATUS_EFFECT: 'sticky_flame_status',
        StatusEffect.STILL_WINDS_STATUS_EFFECT: 'still_winds_status',
        StatusEffect.SWIFTNESS_STATUS_EFFECT: 'swiftness_status',
        StatusEffect.TELEPORT_PREVENTION_STATUS_EFFECT: 'teleport_status',
        StatusEffect.TELEPORT_STATUS_EFFECT: 'teleport_prevention_status',
        StatusEffect.TORNADO_STATUS_EFFECT: 'tornado_status',
        StatusEffect.TRANSMUTATIONS_STATUS_EFFECT: 'transmutations_status',
        StatusEffect.UMBRA_STATUS_EFFECT: 'umbra_status',
        StatusEffect.VITALISATION_STATUS_EFFECT: 'vitalisation_status',
        StatusEffect.VULNERABLE_STATUS_EFFECT: 'vulnerable_status',
        StatusEffect.WATER_STATUS_EFFECT: 'water_status',
        StatusEffect.WEAK_STATUS_EFFECT: 'weak_status',

    }
