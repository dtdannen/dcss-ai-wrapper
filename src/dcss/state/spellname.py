from enum import Enum


class SpellName(Enum):

    """
    Represents a spell
    """

    ABSOLUTE_ZERO = 2
    AGONY = 3
    AIRSTRIKE = 4
    ALISTAIRS_INTOXICATION = 5
    ANIMATE_DEAD = 6
    ANIMATE_SKELETON = 7
    APPORTATION = 8
    AURA_OF_ABJURATION = 9
    BEASTLY_APPENDAGE = 10
    BLADE_HANDS = 11
    BLINK = 12
    BOLT_OF_MAGMA = 13
    BORGNJORS_REVIVIFICATION = 14
    BORGNJORS_VILE_CLUTCH = 15
    CALL_CANINE_FAMILIAR = 16
    CALL_IMP = 17
    CAUSE_FEAR = 18
    CHAIN_LIGHTNING = 19
    CONFUSING_TOUCH = 20
    CONJURE_BALL_LIGHTNING = 21
    CONJURE_FLAME = 22
    CONTROLLED_BLINK = 23
    CORONA = 24
    CORPSE_ROT = 25
    DAZZLING_FLASH = 26
    DEATH_CHANNEL = 27
    DEATHS_DOOR = 28
    DISCORD = 29
    DISJUNCTION = 30
    DISPEL_UNDEAD = 31
    DISPERSAL = 32
    DRAGON_FORM = 33
    DRAGONS_CALL = 34
    ENSORCELLED_HIBERNATION = 35
    ERINGYAS_NOXIOUS_BOG = 36
    EXCRUCIATING_WOUNDS = 37
    FIRE_STORM = 38
    FIREBALL = 39
    FOXFIRE = 40
    FREEZE = 41
    FREEZING_CLOUD = 42
    FROZEN_RAMPARTS = 43
    FULMINANT_PRISM = 44
    GELLS_GRAVITAS = 45
    HAILSTORM = 46
    HAUNT = 47
    HYDRA_FORM = 48
    ICE_FORM = 49
    IGNITE_POISON = 50
    IGNITION = 51
    INFESTATION = 52
    INFUSION = 53
    INNER_FLAME = 54
    INVISIBILITY = 55
    IRON_SHOT = 56
    IRRADIATE = 57
    ISKENDERUNS_BATTLESPHERE = 58
    ISKENDERUNS_MYSTIC_BLAST = 59
    LEDAS_LIQUEFACTION = 60
    LEES_RAPID_DECONSTRUCTION = 61
    LEHUDIBS_CRYSTAL_SPEAR = 62
    LESSER_BECKONING = 63
    LIGHTNING_BOLT = 64
    MAGIC_DART = 65
    MALIGN_GATEWAY = 66
    MEPHITIC_CLOUD = 67
    METABOLIC_ENGLACIATION = 68
    MONSTROUS_MENAGERIE = 69
    NECROMUTATION = 70
    OLGREBS_TOXIC_RADIANCE = 71
    ORB_OF_DESTRUCTION = 72
    OZOCUBUS_ARMOUR = 73
    OZOCUBUS_REFRIGERATION = 74
    PAIN = 75
    PASSAGE_OF_GOLUBRIA = 76
    PASSWALL = 77
    PETRIFY = 78
    POISONOUS_VAPOURS = 79
    PORTAL_PROJECTILE = 80
    RECALL = 81
    RING_OF_FLAMES = 82
    SANDBLAST = 83
    SEARING_RAY = 84
    SHADOW_CREATURES = 85
    SHATTER = 86
    SHOCK = 87
    SHROUD_OF_GOLUBRIA = 88
    SILENCE = 89
    SIMULACRUM = 90
    SLOW = 91
    SONG_OF_SLAYING = 92
    SPECTRAL_WEAPON = 93
    SPELLFORGED_SERVITOR = 94
    SPIDER_FORM = 95
    STARBURST = 96
    STATIC_DISCHARGE = 97
    STATUE_FORM = 98
    STICKS_TO_SNAKES = 99
    STICKY_FLAME = 100
    STING = 101
    STONE_ARROW = 102
    SUBLIMATION_OF_BLOOD = 103
    SUMMON_DEMON = 104
    SUMMON_FOREST = 105
    SUMMON_GREATER_DEMON = 106
    SUMMON_GUARDIAN_GOLEM = 107
    SUMMON_HORRIBLE_THINGS = 108
    SUMMON_HYDRA = 109
    SUMMON_ICE_BEAST = 110
    SUMMON_LIGHTNING_SPIRE = 111
    SUMMON_MANA_VIPER = 112
    SUMMON_SMALL_MAMMAL = 113
    SWIFTNESS = 114
    TELEPORT_OTHER = 115
    TORNADO = 116
    TUKIMAS_DANCE = 117
    VAMPIRIC_DRAINING = 118
    YARAS_VIOLENT_UNRAVELLING = 119


class SpellTypeMapping:

    """
    Assists parsing what spell the player has from websocket data
    """

    spell_game_text_lookup = {

        "Absolute Zero": SpellName.ABSOLUTE_ZERO,
        "Agony": SpellName.AGONY,
        "Airstrike": SpellName.AIRSTRIKE,
        "Alistair's Intoxication": SpellName.ALISTAIRS_INTOXICATION,
        "Animate Dead": SpellName.ANIMATE_DEAD,
        "Animate Skeleton": SpellName.ANIMATE_SKELETON,
        "Apportation": SpellName.APPORTATION,
        "Aura of Abjuration": SpellName.AURA_OF_ABJURATION,
        "Beastly Appendage": SpellName.BEASTLY_APPENDAGE,
        "Blade Hands": SpellName.BLADE_HANDS,
        "Blink": SpellName.BLINK,
        "Bolt of Magma": SpellName.BOLT_OF_MAGMA,
        "Borgnjor's Revivification": SpellName.BORGNJORS_REVIVIFICATION,
        "Borgnjor's Vile Clutch": SpellName.BORGNJORS_VILE_CLUTCH,
        "Call Canine Familiar": SpellName.CALL_CANINE_FAMILIAR,
        "Call Imp": SpellName.CALL_IMP,
        "Cause Fear": SpellName.CAUSE_FEAR,
        "Chain Lightning": SpellName.CHAIN_LIGHTNING,
        "Confusing Touch": SpellName.CONFUSING_TOUCH,
        "Conjure Ball Lightning": SpellName.CONJURE_BALL_LIGHTNING,
        "Conjure Flame": SpellName.CONJURE_FLAME,
        "Controlled Blink": SpellName.CONTROLLED_BLINK,
        "Corona": SpellName.CORONA,
        "Corpse Rot": SpellName.CORPSE_ROT,
        "Dazzling Flash": SpellName.DAZZLING_FLASH,
        "Death Channel": SpellName.DEATH_CHANNEL,
        "Death's Door": SpellName.DEATHS_DOOR,
        "Discord": SpellName.DISCORD,
        "Disjunction": SpellName.DISJUNCTION,
        "Dispel Undead": SpellName.DISPEL_UNDEAD,
        "Dispersal": SpellName.DISPERSAL,
        "Dragon Form": SpellName.DRAGON_FORM,
        "Dragon's Call": SpellName.DRAGONS_CALL,
        "Ensorcelled Hibernation": SpellName.ENSORCELLED_HIBERNATION,
        "Eringya's Noxious Bog": SpellName.ERINGYAS_NOXIOUS_BOG,
        "Excruciating Wounds": SpellName.EXCRUCIATING_WOUNDS,
        "Fire Storm": SpellName.FIRE_STORM,
        "Fireball": SpellName.FIREBALL,
        "Foxfire": SpellName.FOXFIRE,
        "Freeze": SpellName.FREEZE,
        "Freezing Cloud": SpellName.FREEZING_CLOUD,
        "Frozen Ramparts": SpellName.FROZEN_RAMPARTS,
        "Fulminant Prism": SpellName.FULMINANT_PRISM,
        "Gell's Gravitas": SpellName.GELLS_GRAVITAS,
        "Hailstorm": SpellName.HAILSTORM,
        "Haunt": SpellName.HAUNT,
        "Hydra Form": SpellName.HYDRA_FORM,
        "Ice Form": SpellName.ICE_FORM,
        "Ignite Poison": SpellName.IGNITE_POISON,
        "Ignition": SpellName.IGNITION,
        "Infestation": SpellName.INFESTATION,
        "Infusion": SpellName.INFUSION,
        "Inner Flame": SpellName.INNER_FLAME,
        "Invisibility": SpellName.INVISIBILITY,
        "Iron Shot": SpellName.IRON_SHOT,
        "Irradiate": SpellName.IRRADIATE,
        "Iskenderun's Battlesphere": SpellName.ISKENDERUNS_BATTLESPHERE,
        "Iskenderun's Mystic Blast": SpellName.ISKENDERUNS_MYSTIC_BLAST,
        "Leda's Liquefaction": SpellName.LEDAS_LIQUEFACTION,
        "Lee's Rapid Deconstruction": SpellName.LEES_RAPID_DECONSTRUCTION,
        "Lehudib's Crystal Spear": SpellName.LEHUDIBS_CRYSTAL_SPEAR,
        "Lesser Beckoning": SpellName.LESSER_BECKONING,
        "Lightning Bolt": SpellName.LIGHTNING_BOLT,
        "Magic Dart": SpellName.MAGIC_DART,
        "Malign Gateway": SpellName.MALIGN_GATEWAY,
        "Mephitic Cloud": SpellName.MEPHITIC_CLOUD,
        "Metabolic Englaciation": SpellName.METABOLIC_ENGLACIATION,
        "Monstrous Menagerie": SpellName.MONSTROUS_MENAGERIE,
        "Necromutation": SpellName.NECROMUTATION,
        "Olgreb's Toxic Radiance": SpellName.OLGREBS_TOXIC_RADIANCE,
        "Orb of Destruction": SpellName.ORB_OF_DESTRUCTION,
        "Ozocubu's Armour": SpellName.OZOCUBUS_ARMOUR,
        "Ozocubu's Refrigeration": SpellName.OZOCUBUS_REFRIGERATION,
        "Pain": SpellName.PAIN,
        "Passage of Golubria": SpellName.PASSAGE_OF_GOLUBRIA,
        "Passwall": SpellName.PASSWALL,
        "Petrify": SpellName.PETRIFY,
        "Poisonous Vapours": SpellName.POISONOUS_VAPOURS,
        "Portal Projectile": SpellName.PORTAL_PROJECTILE,
        "Recall": SpellName.RECALL,
        "Ring of Flames": SpellName.RING_OF_FLAMES,
        "Sandblast": SpellName.SANDBLAST,
        "Searing Ray": SpellName.SEARING_RAY,
        "Shadow Creatures": SpellName.SHADOW_CREATURES,
        "Shatter": SpellName.SHATTER,
        "Shock": SpellName.SHOCK,
        "Shroud of Golubria": SpellName.SHROUD_OF_GOLUBRIA,
        "Silence": SpellName.SILENCE,
        "Simulacrum": SpellName.SIMULACRUM,
        "Slow": SpellName.SLOW,
        "Song of Slaying": SpellName.SONG_OF_SLAYING,
        "Spectral Weapon": SpellName.SPECTRAL_WEAPON,
        "Spellforged Servitor": SpellName.SPELLFORGED_SERVITOR,
        "Spider Form": SpellName.SPIDER_FORM,
        "Starburst": SpellName.STARBURST,
        "Static Discharge": SpellName.STATIC_DISCHARGE,
        "Statue Form": SpellName.STATUE_FORM,
        "Sticks to Snakes": SpellName.STICKS_TO_SNAKES,
        "Sticky Flame": SpellName.STICKY_FLAME,
        "Sting": SpellName.STING,
        "Stone Arrow": SpellName.STONE_ARROW,
        "Sublimation of Blood": SpellName.SUBLIMATION_OF_BLOOD,
        "Summon Demon": SpellName.SUMMON_DEMON,
        "Summon Forest": SpellName.SUMMON_FOREST,
        "Summon Greater Demon": SpellName.SUMMON_GREATER_DEMON,
        "Summon Guardian Golem": SpellName.SUMMON_GUARDIAN_GOLEM,
        "Summon Horrible Things": SpellName.SUMMON_HORRIBLE_THINGS,
        "Summon Hydra": SpellName.SUMMON_HYDRA,
        "Summon Ice Beast": SpellName.SUMMON_ICE_BEAST,
        "Summon Lightning Spire": SpellName.SUMMON_LIGHTNING_SPIRE,
        "Summon Mana Viper": SpellName.SUMMON_MANA_VIPER,
        "Summon Small Mammal": SpellName.SUMMON_SMALL_MAMMAL,
        "Swiftness": SpellName.SWIFTNESS,
        "Teleport Other": SpellName.TELEPORT_OTHER,
        "Tornado": SpellName.TORNADO,
        "Tukima's Dance": SpellName.TUKIMAS_DANCE,
        "Vampiric Draining": SpellName.VAMPIRIC_DRAINING,
        "Yara's Violent Unravelling": SpellName.YARAS_VIOLENT_UNRAVELLING}