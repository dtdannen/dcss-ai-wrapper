from enum import Enum


class ItemProperty(Enum):
    """
    See crawl wiki for lists of these:
    weapons: http://crawl.chaosforge.org/Brand
    armour: http://crawl.chaosforge.org/Ego
    """
    NO_PROPERTY = 0

    # Melee Weapon Brands
    Antimagic_Brand = 1
    Chaos_Brand = 2
    Disruption_Brand = 3
    Distortion_Brand = 4
    Dragon_slaying_Brand = 5
    Draining_Brand = 6
    Electrocution_Brand = 7
    Flaming_Brand = 8
    Freezing_Brand = 9
    Holywrath_Brand = 10
    Pain_Brand = 11
    Necromancy_Brand = 12
    Protection_Brand = 13
    Reaping_Brand = 14
    Speed_Brand = 15
    Vampiricism_Brand = 16
    Venom_Brand = 17
    Vorpal_Brand = 18

    # Thrown weapon brands
    Dispersal_Brand = 19
    Exploding_Brand = 20
    Penetration_Brand = 21
    Poisoned_Brand = 22
    Returning_Brand = 23
    Silver_Brand = 24
    Steel_Brand = 25

    # Needles
    Confusion_Brand = 26
    Curare_Brand = 27
    Frenzy_Brand = 28
    Paralysis_Brand = 29
    Sleeping_Brand = 30

    # Armour Properties (Egos)
    Resistance_Ego = 31
    Fire_Resistance_Ego = 32
    Cold_Resistance_Ego = 33
    Poison_Resistance_Ego = 34
    Positive_Energy_Ego = 35
    Protection_Ego = 36
    Invisibility_Ego = 37
    Magic_Resistance_Ego = 38
    Strength_Ego = 39
    Dexterity_Ego = 40
    Intelligence_Ego = 41
    Running_Ego = 42
    Flight_Ego = 43
    Stealth_Ego = 44
    See_Invisible_Ego = 45
    Archmagi_Ego = 46
    Ponderousness_Ego = 47
    Reflection_Ego = 48
    Spirit_Shield_Ego = 49
    Archery_Ego = 50