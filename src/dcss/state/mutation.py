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
    }



















