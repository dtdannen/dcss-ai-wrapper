import string
from enum import Enum

class Monster:
    """

    Sample monster data:

    'mon': {
        'id': 1,
        'name': 'kobold',
        'plural': 'kobolds',
        'type': 187,
        'typedata': {
            'avghp': 3
        },
        'att': 0,
        'btype': 187,
        'threat': 1
    }


    """

    all_possible_g_values = string.ascii_lowercase + string.ascii_uppercase + ';'

    # current theory: each monster has a unique id, so use this class variable to track them
    ids_to_monsters = {}

    def __init__(self):
        self.name = None
        self.vals = None
        self.ascii_sym = None
        self.id = None
        self.cell = None  # if the monster is on a cell, update it here (note that this could become outdated and we wouldn't know about it)
        self.threat = 0
        self.type = None
        self.danger_rating = None
        self.health = None
        self.ac = None
        self.ev = None
        self.mr = None

    @staticmethod
    def create_or_update_monster(vals, ascii_sym):
        if 'id' in vals.keys():
            # check if id already exists, if so, retrieve that Monster instance
            mon_id = vals['id']
            if mon_id in Monster.ids_to_monsters.keys():
                # if this monster already exists, update instead of creating new one
                Monster.ids_to_monsters[mon_id].update(vals, ascii_sym)
                return Monster.ids_to_monsters[mon_id]
            else:
                # create a new monster and insert into Monster.ids_to_monsters
                new_monster = Monster()
                new_monster.update(vals, ascii_sym)
                Monster.ids_to_monsters[new_monster.id] = new_monster
                return new_monster
        elif 'name' in vals.keys() and vals['name'] == 'plant':
            # a plant is not a monster
            return 'plant'
        elif 'name' in vals.keys():
            # create a new monster and don't give it an ID (IDs are reserved for the game to give us)
            new_monster = Monster()
            new_monster.update(vals, ascii_sym)
            return new_monster
        else:
            raise Exception("Monster with no id, here's the vals: {}".format(vals))

    def update(self, vals, ascii_sym):
        self.vals = vals
        self.ascii_sym = ascii_sym
        if 'id' in vals.keys():
            self.id = vals['id']

        if 'name' in vals.keys():
            self.name = vals['name'].replace(' ', '_')

        if 'type' in vals.keys():
            self.type = vals['type']

        if 'threat' in vals.keys():
            self.threat = vals['threat']

    def set_cell(self, cell):
        self.cell = cell

    def remove_cell(self):
        # this should happen when a monster dies or is no longer in view
        self.cell = None

    def get_pddl_strs(self, pddl_cell_str):
        """
            (hasmonster ?cell - cell ?monster - monster)
            (monster_danger_rating ?cell - cell ?danger - danger_rating)
            (monster_health ?cell - cell ?amount - qualitative_quantity)
            (monster_status_effect ?cell - cell ?status - status_effect)
        """
        print("about to write hasmonster with name: {}".format(self.name))
        strs = [
            "(hasmonster {} {})".format(pddl_cell_str, self.name),
        ]

        # TODO - also return other monster pddl strings:
        #         (monster_danger_rating ?cell - cell ?danger - danger_rating)
        #         (monster_health ?cell - cell ?amount - qualitative_quantity)
        #         (monster_status_effect ?cell - cell ?status - status_effect)

        return strs

    def set_health(self, health:int):
        self.health = health

    def set_danger_rating(self, danger_rating:str):
        self.danger_rating = danger_rating

    def set_ac(self, ac: int):
        self.ac = ac

    def set_ev(self, ev: int):
        self.ev = ev

    def set_mr(self, mr: int):
        self.mr = mr

    def get_monster_vector(self):
        """
            Returns a vector of a monster with the following fields:

                +--------------+---------------------------------------+------------------------+
                | Vector Index | Description of Data                   | Data Type if available |
                +==============+=======================================+========================+
                +--------------+---------------------------------------+------------------------+
                |     0        |         Monster Type                  | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |     1        | (TODO) Monster is unique              |    Boolean             |
                +--------------+---------------------------------------+------------------------+
                |   2          |       Monster danger rating           |   Int                  |
                +--------------+---------------------------------------+------------------------+
                |   3          |       Monster current health          |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   4          |       Monster max health              |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   5          |       Monster AC                      |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   6          |       Monster EV                      |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   7          |       Monster MR                      |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   8          |       Monster Speed                   |     Int                |
                +--------------+---------------------------------------+------------------------+
                |   9          |       Monster Status Effect 1         | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   10         |       Monster Status Effect 2         | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   11         |       Monster Status Effect 3         | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   12         |       Monster Status Effect 4         | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   13         |       Monster Status Effect 5         | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   14         |       Monster Has Spell 1             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   15         |       Monster Has Spell 2             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   16         |       Monster Has Spell 3             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   17         |       Monster Has Spell 4             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   18         |       Monster Has Spell 5             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+
                |   19         |       Monster Has Spell 6             | Int repr. type ID      |
                +--------------+---------------------------------------+------------------------+

        """
        return [self.type]

    def __str__(self):
        s = ""
        if self.vals:
            s += "Monster vals: \n"
            for v in self.vals:
                s += "\t{}: {}\n".format(v, self.vals[v])

        s += "\n\tAdditional Monster Details:\n"
        s += "\tHealth: {}\n".format(self.health)
        s += "\tac: {}\n".format(self.ac)
        s += "\tev: {}\n".format(self.ev)
        s += "\tmr: {}\n".format(self.mr)
        s += "\tdanger_rating: {}\n".format(self.danger_rating)

        return s


class MonsterName(Enum):

    """
        Monster name that matches the lowercase pddl repr.
    """

    ABOMINATION = 1
    ACID_BLOB = 2
    ACID_DRAGON = 3
    ADDER = 4
    AGATE_SNAIL = 5
    AGNES = 6
    AIR_ELEMENTAL = 7
    AIZUL = 8
    ALLIGATOR = 9
    ALLIGATOR_SNAPPING_TURTLE = 10
    ANACONDA = 11
    ANCIENT_BEAR = 12
    ANCIENT_CHAMPION = 13
    ANCIENT_LICH = 14
    ANCIENT_ZYME = 15
    ANGEL = 16
    ANT_LARVA = 17
    ANTAEUS = 18
    ANUBIS_GUARD = 19
    APIS = 20
    APOCALYPSE_CRAB = 21
    ARACHNE = 22
    ARCHER_STATUE = 23
    ASMODEUS = 24
    ASTERION = 25
    AZRAEL = 26
    AZURE_JELLY = 27
    BABY_ALLIGATOR = 28
    BAI_SUZHEN = 29
    BALL_LIGHTNING = 30
    BALL_PYTHON = 31
    BALLISTOMYCETE = 32
    BALLISTOMYCETE_SPORE = 33
    BALRUG = 34
    BARACHI_MONSTER = 35
    BASILISK = 36
    BAT = 37
    BATTLESPHERE = 38
    BENNU = 39
    BIG_FISH = 40
    BIG_KOBOLD = 41
    BLACK_BEAR = 42
    BLACK_DRACONIAN = 43
    BLACK_MAMBA = 44
    BLACK_SUN = 45
    BLINK_FROG = 46
    BLIZZARD_DEMON = 47
    BLOATED_HUSK = 48
    BLOCK_OF_ICE = 49
    BLOOD_SAINT = 50
    BLORK_THE_ORC = 51
    BLUE_DEATH = 52
    BLUE_DEVIL = 53
    BOG_BODY = 54
    BOG_MUMMY = 55
    BOGGART = 56
    BONE_DRAGON = 57
    BORING_BEETLE = 58
    BORIS = 59
    BOULDER_BEETLE = 60
    BRAIN_WORM = 61
    BRIAR_PATCH = 62
    BRIMSTONE_FIEND = 63
    BROWN_OOZE = 64
    BULLFROG = 65
    BUMBLEBEE = 66
    BUNYIP = 67
    BURNING_BUSH = 68
    BUTTERFLY = 69
    CACODEMON = 70
    CANE_TOAD = 71
    CATOBLEPAS = 72
    CAUSTIC_SHRIKE = 73
    CENTAUR_MONSTER = 74
    CENTAUR_WARRIOR = 75
    CEREBOV = 76
    CHAOS_BUTTERFLY = 77
    CHAOS_CHAMPION = 78
    CHAOS_SPAWN = 79
    CHARRED_STATUE = 80
    CHERUB = 81
    CHIMERA = 82
    CHUCK = 83
    CLAY_GOLEM = 84
    CONJURER_STATUE = 85
    CORRUPTER = 86
    CRAWLING_CORPSE = 87
    CRAZY_YIUF = 88
    CRIMSON_IMP = 89
    CROCODILE = 90
    CRYSTAL_GOLEM = 91
    CRYSTAL_GUARDIAN = 92
    CURSE_SKULL = 93
    CURSE_TOE = 94
    CYCLOPS = 95
    DAEVA = 96
    DANCING_WEAPON = 97
    DART_SLUG = 98
    DEATH_COB = 99
    DEATH_DRAKE = 100
    DEATH_KNIGHT = 101
    DEATH_OOZE = 102
    DEATH_SCARAB = 103
    DEATH_YAK = 104
    DEATHCAP = 105
    DEEP_DWARF_MONSTER = 106
    DEEP_DWARF_ARTIFICER = 107
    DEEP_DWARF_BERSERKER = 108
    DEEP_DWARF_DEATH_KNIGHT = 109
    DEEP_DWARF_NECROMANCER = 110
    DEEP_DWARF_SCION = 111
    DEEP_ELF_ANNIHILATOR = 112
    DEEP_ELF_ARCHER = 113
    DEEP_ELF_BLADEMASTER = 114
    DEEP_ELF_CONJURER = 115
    DEEP_ELF_DEATH_MAGE = 116
    DEEP_ELF_DEMONOLOGIST = 117
    DEEP_ELF_ELEMENTALIST = 118
    DEEP_ELF_FIGHTER = 119
    DEEP_ELF_HIGH_PRIEST = 120
    DEEP_ELF_KNIGHT = 121
    DEEP_ELF_MAGE = 122
    DEEP_ELF_MASTER_ARCHER = 123
    DEEP_ELF_PRIEST = 124
    DEEP_ELF_SOLDIER = 125
    DEEP_ELF_SORCERER = 126
    DEEP_ELF_SUMMONER = 127
    DEEP_TROLL = 128
    DEEP_TROLL_EARTH_MAGE = 129
    DEEP_TROLL_SHAMAN = 130
    DEMIGOD_MONSTER = 131
    DEMON = 132
    DEMONIC_CRAWLER = 133
    DEMONIC_MONSTERS = 134
    DEMONSPAWN_MONSTER = 135
    DERIVED_UNDEAD = 136
    DIAMOND_OBELISK = 137
    DIRE_ELEPHANT = 138
    DISPATER = 139
    DISSOLUTION = 140
    DONALD = 141
    DOOM_HOUND = 142
    DOWAN = 143
    DRACONIAN_MONSTER = 144
    DRACONIAN_ANNIHILATOR = 145
    DRACONIAN_KNIGHT = 146
    DRACONIAN_MONK = 147
    DRACONIAN_SCORCHER = 148
    DRACONIAN_SHIFTER = 149
    DRACONIAN_STORMCALLER = 150
    DRACONIAN_ZEALOT = 151
    DREAM_SHEEP = 152
    DROWNED_SOUL = 153
    DRYAD = 154
    DUANE = 155
    DUVESSA = 156
    DWARF = 157
    EARTH_ELEMENTAL = 158
    EDMUND = 159
    EFREET = 160
    EIDOLON = 161
    ELDRITCH_TENTACLE = 162
    ELECTRIC_EEL = 163
    ELECTRIC_GOLEM = 164
    ELEIONOMA = 165
    ELEMENTAL_WELLSPRING = 166
    ELEPHANT = 167
    ELEPHANT_SLUG = 168
    ELF = 169
    EMPEROR_SCORPION = 170
    ENTROPY_WEAVER = 171
    ERESHKIGAL = 172
    ERICA = 173
    EROLCHA = 174
    ETTIN = 175
    EUSTACHIO = 176
    EXECUTIONER = 177
    EYE_OF_DEVASTATION = 178
    EYE_OF_DRAINING = 179
    FANNAR = 180
    FAUN = 181
    FELID_MONSTER = 182
    FENSTRIDER_WITCH = 183
    FIRE_BAT = 184
    FIRE_CRAB = 185
    FIRE_DRAGON = 186
    FIRE_DRAKE = 187
    FIRE_ELEMENTAL = 188
    FIRE_GIANT = 189
    FIRE_VORTEX = 190
    FIRESPITTER_STATUE = 191
    FLAMING_CORPSE = 192
    FLAYED_GHOST = 193
    FLOATING_EYE = 194
    FLYING_SKULL = 195
    FORMICID_MONSTER = 196
    FORMICID_DRONE = 197
    FORMICID_VENOM_MAGE = 198
    FRANCES = 199
    FRANCIS = 200
    FREDERICK = 201
    FREEZING_WRAITH = 202
    FRILLED_LIZARD = 203
    FROST_GIANT = 204
    FROST_COVERED_STATUE = 205
    GARGOYLE_MONSTER = 206
    GASTRONOK = 207
    GELID_DEMONSPAWN = 208
    GERYON = 209
    GHOST_CRAB = 210
    GHOST_MOTH = 211
    GHOUL_MONSTER = 212
    GIANT_AMOEBA = 213
    GIANT_BLOWFLY = 214
    GIANT_CENTIPEDE = 215
    GIANT_COCKROACH = 216
    GIANT_FIREFLY = 217
    GIANT_GOLDFISH = 218
    GIANT_MITE = 219
    GIANT_SLUG = 220
    GIANT_TOAD = 221
    GILA_MONSTER = 222
    GLOORX_VLOQ = 223
    GLOWING_ORANGE_BRAIN = 224
    GLOWING_SHAPESHIFTER = 225
    GNOLL_MONSTER = 226
    GNOLL_SERGEANT = 227
    GNOLL_SHAMAN = 228
    GOBLIN = 229
    GOLDEN_DRAGON = 230
    GOLDEN_EYE = 231
    GOLIATH_BEETLE = 232
    GOLIATH_FROG = 233
    GRAND_AVATAR_MONSTER = 234
    GREAT_ORB_OF_EYES = 235
    GREEN_DEATH = 236
    GREEN_DRACONIAN = 237
    GREY_DRACONIAN = 238
    GREY_RAT = 239
    GRIFFON = 240
    GRINDER = 241
    GRIZZLY_BEAR = 242
    GRUM = 243
    GUARDIAN_GOLEM = 244
    GUARDIAN_MUMMY = 245
    GUARDIAN_NAGA = 246
    GUARDIAN_SERPENT = 247
    HAIRY_DEVIL = 248
    HALAZID_WARLOCK = 249
    HALFLING_MONSTER = 250
    HAROLD = 251
    HARPY = 252
    HELL_BEAST = 253
    HELL_HOG = 254
    HELL_HOUND = 255
    HELL_KNIGHT = 256
    HELL_RAT = 257
    HELL_SENTINEL = 258
    HELLEPHANT = 259
    HELLION = 260
    HELLWING = 261
    HILL_GIANT = 262
    HIPPOGRIFF = 263
    HOBGOBLIN = 264
    HOG = 265
    HOLY_SWINE = 266
    HORNET = 267
    HOUND = 268
    HOWLER_MONKEY = 269
    HUMAN_MONSTER = 270
    HUNGRY_GHOST = 271
    HYDRA = 272
    ICE_BEAST = 273
    ICE_DEVIL = 274
    ICE_DRAGON = 275
    ICE_FIEND = 276
    ICE_STATUE = 277
    IGNACIO = 278
    IGNIS = 279
    IGUANA = 280
    IJYB = 281
    ILSUIW = 282
    IMPERIAL_MYRMIDON = 283
    INEPT_MIMIC = 284
    INFERNAL_DEMONSPAWN = 285
    INSUBSTANTIAL_WISP = 286
    IRON_DEVIL = 287
    IRON_DRAGON = 288
    IRON_ELEMENTAL = 289
    IRON_GIANT = 290
    IRON_GOLEM = 291
    IRON_IMP = 292
    IRON_TROLL = 293
    IRONBRAND_CONVOKER = 294
    IRONHEART_PRESERVER = 295
    JACKAL = 296
    JELLY = 297
    JELLYFISH = 298
    JESSICA = 299
    JIANGSHI = 300
    JORGRUN = 301
    JORY = 302
    JOSEPH = 303
    JOSEPHINE = 304
    JOZEF = 305
    JUGGERNAUT = 306
    JUMPING_SPIDER = 307
    KHUFU = 308
    KILLER_BEE = 309
    KILLER_BEE_LARVA = 310
    KILLER_KLOWN = 311
    KIRKE = 312
    KOBOLD_MONSTER = 313
    KOBOLD_DEMONOLOGIST = 314
    KOMODO_DRAGON = 315
    KRAKEN = 316
    LABORATORY_RAT = 317
    LAMIA = 318
    LARGE_ABOMINATION = 319
    LASHER_STATUE = 320
    LAVA_FISH = 321
    LAVA_SNAKE = 322
    LAVA_WORM = 323
    LEMURE = 324
    LEOPARD_GECKO = 325
    LICH = 326
    LIGHTNING_SPIRE = 327
    LINDWURM = 328
    LIST_OF_MONSTERS = 329
    LOM_LOBON = 330
    LOROCYPROCA = 331
    LOST_SOUL = 332
    LOUISE = 333
    LURKING_HORROR = 334
    MACABRE_MASS = 335
    MAGGIE = 336
    MANA_VIPER = 337
    MANTICORE = 338
    MARA = 339
    MARGERY = 340
    MASTER_BLASTER = 341
    MASTER_ELEMENTALIST = 342
    MAUD = 343
    MAURICE = 344
    MELIAI = 345
    MENKAURE = 346
    MENNAS = 347
    MERFOLK = 348
    MERFOLK_MONSTER = 349
    MERFOLK_AQUAMANCER = 350
    MERFOLK_AVATAR = 351
    MERFOLK_IMPALER = 352
    MERFOLK_JAVELINEER = 353
    MERFOLK_SIREN = 354
    MERMAID = 355
    METAL_GARGOYLE = 356
    MICHAEL = 357
    MIDGE = 358
    MIMIC_MONSTER = 359
    MINOTAUR_MONSTER = 360
    MNOLEG = 361
    MOLTEN_GARGOYLE = 362
    MONSTER_ATTRIBUTES = 363
    MONSTER_GENERATION = 364
    MONSTERS = 365
    MONSTROUS_DEMONSPAWN = 366
    MOTH_OF_SUPPRESSION = 367
    MOTH_OF_WRATH = 368
    MOTTLED_DRACONIAN = 369
    MOTTLED_DRAGON = 370
    MUMMY_MONSTER = 371
    MUMMY_PRIEST = 372
    MURRAY = 373
    NAGA_MONSTER = 374
    NAGA_MAGE = 375
    NAGA_RITUALIST = 376
    NAGA_SHARPSHOOTER = 377
    NAGA_WARRIOR = 378
    NAGARAJA = 379
    NAMELESS_HORROR = 380
    NATASHA = 381
    NECROMANCER_MONSTER = 382
    NECROPHAGE = 383
    NELLIE = 384
    NEQOXEC = 385
    NERGALLE = 386
    NESSOS = 387
    NIKOLA = 388
    NORBERT = 389
    NORRIS = 390
    OBSIDIAN_STATUE = 391
    OCTOPODE_MONSTER = 392
    OCTOPODE_CRUSHER = 393
    OGRE_MONSTER = 394
    OGRE_MAGE = 395
    OKLOB_PLANT = 396
    OKLOB_SAPLING = 397
    OOZE = 398
    OPHAN = 399
    ORANGE_CRYSTAL_STATUE = 400
    ORANGE_DEMON = 401
    ORB_GUARDIAN = 402
    ORB_OF_FIRE = 403
    ORB_SPIDER = 404
    ORC = 405
    ORC_HIGH_PRIEST = 406
    ORC_KNIGHT = 407
    ORC_PRIEST = 408
    ORC_SORCERER = 409
    ORC_WARLORD = 410
    ORC_WARRIOR = 411
    ORC_WIZARD = 412
    PALADIN_MONSTER = 413
    PALE_DRACONIAN = 414
    PAN_MONSTER = 415
    PANDEMONIUM_LORD = 416
    PEACEKEEPER = 417
    PEARL_DRAGON = 418
    PHANTASMAL_WARRIOR = 419
    PHANTOM = 420
    PHOENIX = 421
    PIKEL = 422
    PILLAR_OF_SALT = 423
    PIT_FIEND = 424
    PLAGUE_SHAMBLER = 425
    POLAR_BEAR = 426
    POLYMOTH = 427
    POLYPHEMUS = 428
    PORCUPINE = 429
    PRIESTS = 430
    PRINCE_RIBBIT = 431
    PROFANE_SERVITOR = 432
    PSYCHE = 433
    PULSATING_LUMP = 434
    PURGY = 435
    PURPLE_DRACONIAN = 436
    PUTRID_DEMONSPAWN = 437
    QUASIT = 438
    QUEEN_ANT = 439
    QUEEN_BEE = 440
    QUICKSILVER_DRAGON = 441
    QUOKKA = 442
    RAGGED_HIEROPHANT = 443
    RAIJU = 444
    RAKSHASA = 445
    RAT = 446
    RAVEN = 447
    RAVENOUS_MIMIC = 448
    REAPER = 449
    RED_DEVIL = 450
    RED_DRACONIAN = 451
    REDBACK = 452
    REVENANT = 453
    RIME_DRAKE = 454
    RIVER_RAT = 455
    ROBIN = 456
    ROCK_TROLL = 457
    ROCK_WORM = 458
    ROTTING_DEVIL = 459
    ROTTING_HULK = 460
    ROXANNE = 461
    ROYAL_MUMMY = 462
    RUPERT = 463
    RUST_DEVIL = 464
    SAINT_ROKA = 465
    SALAMANDER = 466
    SALAMANDER_FIREBRAND = 467
    SALAMANDER_MYSTIC = 468
    SALAMANDER_STORMCALLER = 469
    SALTLING = 470
    SATYR = 471
    SCORPION = 472
    SEA_SNAKE = 473
    SERAPH = 474
    SERPENT_OF_HELL_COCYTUS = 475
    SERPENT_OF_HELL_DIS = 476
    SERPENT_OF_HELL_GEHENNA = 477
    SERPENT_OF_HELL_TARTARUS = 478
    SERVANT_OF_WHISPERS = 479
    SHADOW = 480
    SHADOW_DEMON = 481
    SHADOW_DRAGON = 482
    SHADOW_IMP = 483
    SHADOW_WRAITH = 484
    SHAMBLING_MANGROVE = 485
    SHAPESHIFTER = 486
    SHARD_SHRIKE = 487
    SHARK = 488
    SHEDU = 489
    SHEEP = 490
    SHINING_EYE = 491
    SHOCK_SERPENT = 492
    SIGMUND = 493
    SILENT_SPECTRE = 494
    SILVER_STAR = 495
    SILVER_STATUE = 496
    SIMULACRUM_MONSTER = 497
    SIXFIRHY = 498
    SKELETAL_WARRIOR = 499
    SKELETON_MONSTER = 500
    SKY_BEAST = 501
    SLAVE = 502
    SLIME_CREATURE = 503
    SMALL_ABOMINATION = 504
    SMOKE_DEMON = 505
    SNAIL_STATUE = 506
    SNAPLASHER_VINE = 507
    SNAPPING_TURTLE = 508
    SNORG = 509
    SOJOBO = 510
    SOLDIER_ANT = 511
    SONJA = 512
    SOUL_EATER = 513
    SPARK_WASP = 514
    SPATIAL_MAELSTROM = 515
    SPATIAL_VORTEX = 516
    SPECTRAL_THING = 517
    SPELLFORGED_SERVITOR_MONSTER = 518
    SPHINX = 519
    SPIDER = 520
    SPINY_WORM = 521
    SPIRIT = 522
    SPIRIT_WOLF = 523
    SPOOKY_STATUE = 524
    SPRIGGAN_MONSTER = 525
    SPRIGGAN_AIR_MAGE = 526
    SPRIGGAN_ASSASSIN = 527
    SPRIGGAN_BERSERKER = 528
    SPRIGGAN_DEFENDER = 529
    SPRIGGAN_DRUID = 530
    SPRIGGAN_ENCHANTER = 531
    SPRIGGAN_RIDER = 532
    STARCURSED_MASS = 533
    STEAM_DRAGON = 534
    STONE_GIANT = 535
    STONE_GOLEM = 536
    STORM_DRAGON = 537
    SUBTRACTOR_SNAKE = 538
    SUN_DEMON = 539
    SWAMP_DRAGON = 540
    SWAMP_DRAKE = 541
    SWAMP_WORM = 542
    TARANTELLA = 543
    TENGU_MONSTER = 545
    TENGU_CONJURER = 546
    TENGU_REAVER = 547
    TENGU_WARRIOR = 548
    TENTACLED_MONSTROSITY = 549
    TENTACLED_STARSPAWN = 550
    TERENCE = 551
    TERPSICHORE = 552
    TEST_SPAWNER = 553
    THE_ENCHANTRESS = 554
    THE_IRON_GIANT = 555
    THE_LERNAEAN_HYDRA = 556
    THE_ROYAL_JELLY = 557
    THORN_HUNTER = 558
    THORN_LOTUS = 559
    THRASHING_HORROR = 560
    TIAMAT = 561
    TITAN = 562
    TOADSTOOL = 563
    TOENAIL_GOLEM = 564
    TORMENTOR = 565
    TORPOR_SNAIL = 566
    TORTUROUS_DEMONSPAWN = 567
    TRAINING_DUMMY = 568
    TROLL = 569
    TROLL_MONSTER = 570
    TWISTER = 571
    TWO_HEADED_OGRE = 572
    TYRANT_LEECH = 573
    TZITZIMITL = 574
    UFETUBUS = 575
    UGLY_THING = 576
    UNBORN = 577
    UNBORN_DEEP_DWARF = 578
    UNSEEN_HORROR = 579
    URUG = 580
    USHABTI = 581
    VAMPIRE_MONSTER = 582
    VAMPIRE_BAT = 583
    VAMPIRE_KNIGHT = 584
    VAMPIRE_MAGE = 585
    VAMPIRE_MOSQUITO = 586
    VAPOUR = 587
    VASHNIA = 588
    VAULT_GUARD = 589
    VAULT_SENTINEL = 590
    VAULT_WARDEN = 591
    VERY_UGLY_THING = 592
    VINE_STALKER_MONSTER = 593
    VIPER = 594
    WANDERING_MUSHROOM = 595
    WAR_DOG = 596
    WAR_GARGOYLE = 597
    WARG = 598
    WARMONGER = 599
    WASP = 600
    WATER_ELEMENTAL = 601
    WATER_MOCCASIN = 602
    WATER_NYMPH = 603
    WHITE_DRACONIAN = 604
    WHITE_IMP = 605
    WIGHT = 606
    WIGLAF = 607
    WILL_O_THE_WISP = 608
    WIND_DRAKE = 609
    WIZARD_MONSTER = 610
    WIZARD_STATUE = 611
    WOLF = 612
    WOLF_SPIDER = 613
    WOOD_GOLEM = 614
    WORKER_ANT = 615
    WORLDBINDER = 616
    WORM = 617
    WRAITH = 618
    WRETCHED_STAR = 619
    WYVERN = 620
    XTAHUA = 621
    YAK = 622
    YAKTAUR = 623
    YAKTAUR_CAPTAIN = 624
    YELLOW_DRACONIAN = 625
    YNOXINUL = 626
    ZOMBIE = 627
    ZOT_STATUE = 628