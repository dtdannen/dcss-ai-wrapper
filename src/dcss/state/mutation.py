from enum import Enum


class Mutation(Enum):

    """
    Represents a mutation in the game.
    """

    ACUTE_VISION_MUTATION = 1
    ANTENNAE_MUTATION = 2
    BEAK_MUTATION = 3
    BIG_WINGS_MUTATION = 4
    BLINK_MUTATION = 5
    CAMOUFLAGE_MUTATION = 6
    CLARITY_MUTATION = 7
    CLAWS_MUTATION = 8
    COLD_RESISTANCE_MUTATION = 9
    ELECTRICITY_RESISTANCE_MUTATION = 10
    EVOLUTION_MUTATION = 11
    FANGS_MUTATION = 12
    FIRE_RESISTANCE_MUTATION = 13
    HIGH_MP_MUTATION = 14
    HOOVES_MUTATION = 15
    HORNS_MUTATION = 16
    ICY_BLUE_SCALES_MUTATION = 17
    IMPROVED_ATTRIBUTES_MUTATION = 18
    IRIDESCENT_SCALES_MUTATION = 19
    LARGE_BONE_PLATES_MUTATION = 20
    MAGIC_RESISTANCE_MUTATION = 21
    MOLTEN_SCALES_MUTATION = 22
    MUTATION_RESISTANCE_MUTATION = 23
    PASSIVE_MAPPING_MUTATION = 24
    POISON_BREATH_MUTATION = 25
    POISON_RESISTANCE_MUTATION = 26
    REGENERATION_MUTATION = 27
    REPULSION_FIELD_MUTATION = 28
    ROBUST_MUTATION = 29
    RUGGED_BROWN_SCALES_MUTATION = 30
    SHAGGY_FUR_MUTATION = 31
    SLIMY_GREEN_SCALES_MUTATION = 32
    STINGER_MUTATION = 33
    STRONG_LEGS_MUTATION = 34
    TALONS_MUTATION = 35
    TENTACLE_SPIKE_MUTATION = 36
    THIN_METALLIC_SCALES_MUTATION = 37
    THIN_SKELETAL_STRUCTURE_MUTATION = 38
    TOUGH_SKIN_MUTATION = 39
    WILD_MAGIC_MUTATION = 40
    YELLOW_SCALES_MUTATION = 41
    OFFHAND_PUNCH_AUX_ATK_MUTATION = 101
    OFFHAND_PUNCH_W_CLAWS_AUX_ATK_MUTATION = 102
    OFFHAND_PUNCH_W__BLADE_HANDS_AUX_ATK_MUTATION = 103
    HEADBUTT_AUX_ATK_MUTATION = 104
    PECK_AUX_ATK_MUTATION = 105
    KICK_W_HOOVES_AUX_ATK_MUTATION = 106
    KICK_W_TALONS_AUX_ATK_MUTATION = 107
    TAIL_SLAP_AUX_ATK_MUTATION = 108
    TAIL_SLAP_W_STINGER_AUX_ATK_MUTATION = 109
    BITE_W_FANGS_AUX_ATK_MUTATION = 1010
    BITE_W_ACIDIC_BITE_AUX_ATK_MUTATION = 1011
    BITE_W_ANTI_MAGIC_BITE_AUX_ATK_MUTATION = 1012
    PSEUDOPODS_AUX_ATK_MUTATION = 1013
    TENTACLE_SPIKE_AUX_ATK_MUTATION = 1014
    TENTACLE_SLAP_AUX_ATK_MUTATION = 1015
    TENTACLES_SQUEEZE_AUX_ATK_MUTATION = 1016
    CONSTRICTION_AUX_ATK_MUTATION = 1017


class MutationMapping:

    """
    Assists parsing what mutations the player has from websocket data
    """

    mutation_menu_messages_lookup = {
        "": Mutation.ACUTE_VISION_MUTATION,
        "": Mutation.ANTENNAE_MUTATION,
        "": Mutation.BEAK_MUTATION,
        "": Mutation.BIG_WINGS_MUTATION,
        "": Mutation.BLINK_MUTATION,
        "": Mutation.CAMOUFLAGE_MUTATION,
        "": Mutation.CLARITY_MUTATION,
        "": Mutation.CLAWS_MUTATION,
        "": Mutation.COLD_RESISTANCE_MUTATION,
        "": Mutation.ELECTRICITY_RESISTANCE_MUTATION,
        "": Mutation.EVOLUTION_MUTATION,
        "": Mutation.FANGS_MUTATION,
        "": Mutation.FIRE_RESISTANCE_MUTATION,
        "": Mutation.HIGH_MP_MUTATION,
        "": Mutation.HOOVES_MUTATION,
        "You have a pair of horns on your head": Mutation.HORNS_MUTATION,
        "You are partially covered in icy blue scales": Mutation.ICY_BLUE_SCALES_MUTATION,
        "": Mutation.IMPROVED_ATTRIBUTES_MUTATION,
        "": Mutation.IRIDESCENT_SCALES_MUTATION,
        "": Mutation.LARGE_BONE_PLATES_MUTATION,
        "": Mutation.MAGIC_RESISTANCE_MUTATION,
        "": Mutation.MOLTEN_SCALES_MUTATION,
        "": Mutation.MUTATION_RESISTANCE_MUTATION,
        "": Mutation.PASSIVE_MAPPING_MUTATION,
        "": Mutation.POISON_BREATH_MUTATION,
        "": Mutation.POISON_RESISTANCE_MUTATION,
        "": Mutation.REGENERATION_MUTATION,
        "": Mutation.REPULSION_FIELD_MUTATION,
        "": Mutation.ROBUST_MUTATION,
        "": Mutation.RUGGED_BROWN_SCALES_MUTATION,
        "": Mutation.SHAGGY_FUR_MUTATION,
        "": Mutation.SLIMY_GREEN_SCALES_MUTATION,
        "": Mutation.STINGER_MUTATION,
        "": Mutation.STRONG_LEGS_MUTATION,
        "": Mutation.TALONS_MUTATION,
        "": Mutation.TENTACLE_SPIKE_MUTATION,
        "": Mutation.THIN_METALLIC_SCALES_MUTATION,
        "": Mutation.THIN_SKELETAL_STRUCTURE_MUTATION,
        "": Mutation.TOUGH_SKIN_MUTATION,
        "": Mutation.WILD_MAGIC_MUTATION,
        "": Mutation.YELLOW_SCALES_MUTATION,
        "": Mutation.OFFHAND_PUNCH_AUX_ATK_MUTATION,
        "": Mutation.OFFHAND_PUNCH_W_CLAWS_AUX_ATK_MUTATION,
        "": Mutation.OFFHAND_PUNCH_W__BLADE_HANDS_AUX_ATK_MUTATION,
        "You reflexively headbutt those who attack you in melee": Mutation.HEADBUTT_AUX_ATK_MUTATION,
        "": Mutation.PECK_AUX_ATK_MUTATION,
        "": Mutation.KICK_W_HOOVES_AUX_ATK_MUTATION,
        "": Mutation.KICK_W_TALONS_AUX_ATK_MUTATION,
        "": Mutation.TAIL_SLAP_AUX_ATK_MUTATION,
        "": Mutation.TAIL_SLAP_W_STINGER_AUX_ATK_MUTATION,
        "": Mutation.BITE_W_FANGS_AUX_ATK_MUTATION,
        "": Mutation.BITE_W_ACIDIC_BITE_AUX_ATK_MUTATION,
        "": Mutation.BITE_W_ANTI_MAGIC_BITE_AUX_ATK_MUTATION,
        "": Mutation.PSEUDOPODS_AUX_ATK_MUTATION,
        "": Mutation.TENTACLE_SPIKE_AUX_ATK_MUTATION,
        "": Mutation.TENTACLE_SLAP_AUX_ATK_MUTATION,
        "": Mutation.TENTACLES_SQUEEZE_AUX_ATK_MUTATION,
        "": Mutation.CONSTRICTION_AUX_ATK_MUTATION,
    }


class MutationPDDLMapping:

    """
    Assists writing pddl what mutation the player has
    """

    mutation_pddl_lookup = {
        Mutation.ACUTE_VISION_MUTATION: "acute_vision",
        Mutation.ANTENNAE_MUTATION: "antennae",
        Mutation.BEAK_MUTATION: "beak",
        Mutation.BIG_WINGS_MUTATION: "big_wings",
        Mutation.BLINK_MUTATION: "blink",
        Mutation.CAMOUFLAGE_MUTATION: "camouflage",
        Mutation.CLARITY_MUTATION: "clarity",
        Mutation.CLAWS_MUTATION: "claws",
        Mutation.COLD_RESISTANCE_MUTATION: "cold_resistance",
        Mutation.ELECTRICITY_RESISTANCE_MUTATION: "electricity_resistance",
        Mutation.EVOLUTION_MUTATION: "evolution",
        Mutation.FANGS_MUTATION: "fangs",
        Mutation.FIRE_RESISTANCE_MUTATION: "fire_resistance",
        Mutation.HIGH_MP_MUTATION: "high_mp",
        Mutation.HOOVES_MUTATION: "hooves",
        Mutation.HORNS_MUTATION: "horns",
        Mutation.ICY_BLUE_SCALES_MUTATION: "icy_blue_scales",
        Mutation.IMPROVED_ATTRIBUTES_MUTATION: "improved_attributes",
        Mutation.IRIDESCENT_SCALES_MUTATION: "iridescent_scales",
        Mutation.LARGE_BONE_PLATES_MUTATION: "large_bone_plates",
        Mutation.MAGIC_RESISTANCE_MUTATION: "magic_resistance",
        Mutation.MOLTEN_SCALES_MUTATION: "molten_scales",
        Mutation.MUTATION_RESISTANCE_MUTATION: "mutation_resistance",
        Mutation.PASSIVE_MAPPING_MUTATION: "passive_mapping",
        Mutation.POISON_BREATH_MUTATION: "poison_breath",
        Mutation.POISON_RESISTANCE_MUTATION: "poison_resistance",
        Mutation.REGENERATION_MUTATION: "regeneration",
        Mutation.REPULSION_FIELD_MUTATION: "repulsion_field",
        Mutation.ROBUST_MUTATION: "robust",
        Mutation.RUGGED_BROWN_SCALES_MUTATION: "rugged_brown_scales",
        Mutation.SHAGGY_FUR_MUTATION: "shaggy_fur",
        Mutation.SLIMY_GREEN_SCALES_MUTATION: "slimy_green_scales",
        Mutation.STINGER_MUTATION: "stinger",
        Mutation.STRONG_LEGS_MUTATION: "strong_legs",
        Mutation.TALONS_MUTATION: "talons",
        Mutation.TENTACLE_SPIKE_MUTATION: "tentacle_spike",
        Mutation.THIN_METALLIC_SCALES_MUTATION: "thin_metallic_scales",
        Mutation.THIN_SKELETAL_STRUCTURE_MUTATION: "thin_skeletal_structure",
        Mutation.TOUGH_SKIN_MUTATION: "tough_skin",
        Mutation.WILD_MAGIC_MUTATION: "wild_magic",
        Mutation.YELLOW_SCALES_MUTATION: "yellow_scales",
        Mutation.OFFHAND_PUNCH_AUX_ATK_MUTATION: "offhand_punch_aux_atk",
        Mutation.OFFHAND_PUNCH_W_CLAWS_AUX_ATK_MUTATION: "offhand_punch_w_claws_aux_atk",
        Mutation.OFFHAND_PUNCH_W__BLADE_HANDS_AUX_ATK_MUTATION: "offhand_punch_w__blade_hands_aux_atk",
        Mutation.HEADBUTT_AUX_ATK_MUTATION: "headbutt_aux_atk",
        Mutation.PECK_AUX_ATK_MUTATION: "peck_aux_atk",
        Mutation.KICK_W_HOOVES_AUX_ATK_MUTATION: "kick_w_hooves_aux_atk",
        Mutation.KICK_W_TALONS_AUX_ATK_MUTATION: "kick_w_talons_aux_atk",
        Mutation.TAIL_SLAP_AUX_ATK_MUTATION: "tail_slap_aux_atk",
        Mutation.TAIL_SLAP_W_STINGER_AUX_ATK_MUTATION: "tail_slap_w_stinger_aux_atk",
        Mutation.BITE_W_FANGS_AUX_ATK_MUTATION: "bite_w_fangs_aux_atk",
        Mutation.BITE_W_ACIDIC_BITE_AUX_ATK_MUTATION: "bite_w_acidic_bite_aux_atk",
        Mutation.BITE_W_ANTI_MAGIC_BITE_AUX_ATK_MUTATION: "bite_w_anti_magic_bite_aux_atk",
        Mutation.PSEUDOPODS_AUX_ATK_MUTATION: "pseudopods_aux_atk",
        Mutation.TENTACLE_SPIKE_AUX_ATK_MUTATION: "tentacle_spike_aux_atk",
        Mutation.TENTACLE_SLAP_AUX_ATK_MUTATION: "tentacle_slap_aux_atk",
        Mutation.TENTACLES_SQUEEZE_AUX_ATK_MUTATION: "tentacles_squeeze_aux_atk",
        Mutation.CONSTRICTION_AUX_ATK_MUTATION: "constriction_aux_atk",
    }


















