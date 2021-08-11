;;; File: models/fastdownward_simple.pddl
;;;
;;; Simple domain representation for dungeon crawl stone soup compatible with
;;; the fastdownward planner and other pddl planning systems.
;;;
;;; Author: Dustin Dannenhauer
;;; Email: dannenhauerdustin@gmail.com
;;;
;;; Notes:
;;;     0. This domain file is not meant to accurately represent dungeon crawl
;;;        stone soup. Rather it is meant as a low fidelity approximation
;;;        of the real environment that is meant to be incorporated into a
;;;        planning system embedded in an agent with plan execution monitoring
;;;        and other capabilities, to produce goal-directed behavior capable of
;;;        basic reasoning about most player actions.
;;;
;;;     1. This domain file was created using the best available information
;;;        from the crawl wiki, which is not always kept up to date. Please
;;;        submit an issue on the github if any errors or inconsistencies are
;;;        found. Github: https://github.com/dtdannen/dcss-ai-wrapper
;;;        Crawl wiki: http://crawl.chaosforge.org/


(define (domain dcss)
(:requirements :strips :negative-preconditions :existential-preconditions)
(:types monster - object
        cell - object
        place - object ; examples: zot_4, dungeon_12, vaults_2
        skill - object
        ability - object
        spell - object
        god - object
        qualitative_quantity - object
        status - object
        mutation - object
        terrain - object
        danger_rating - object
        item - object
        rune - object
        status_effect - object
        target_ability_text_message - object

        non_target_based_spell - spell
        target_based_spell - spell

        non_target_ability - ability
        target_ability - ability

        target_ability_location - target_ability
        target_ability_menu - target_ability
        target_ability_text_message_choice - target_ability

        consumeitem - item
        equipitem - item

        potion - consumeitem
        scroll - consumeitem

        weapon - equipitem
        armour - equipitem
)

(:constants
;; background objects

  none - qualitative_quantity
  low - qualitative_quantity
  medium_low - qualitative_quantity
  medium - qualitative_quantity
  medium_high - qualitative_quantity
  high - qualitative_quantity
  maxed - qualitative_quantity

  serpentine_rune - rune
  decaying_rune - rune
  barnacled_rune - rune
  gossamer_rune - rune
  abyssal_rune - rune
  silver_rune - rune
  slimy_rune - rune
  dark_rune - rune
  glowing_rune - rune
  fiery_rune - rune
  magical_rune - rune
  demonic_rune - rune
  golden_rune - rune
  iron_rune - rune
  icy_rune - rune
  obsidian_rune - rune
  bone_rune - rune

  shallow_water - terrain
  deep_water - terrain
  lava - terrain
  rock_wall - terrain
  translucent_rock_wall - terrain
  green_crystal_wall - terrain
  stone_wall - terrain
  translucent_stone_wall - terrain
  metal_wall - terrain
  unnaturally_hard_wall - terrain
  bush - terrain
  fungus - terrain
  plant - terrain
  trees - terrain

  easy - danger_rating
  dangerous - danger_rating
  very_dangerous - danger_rating

  abomination - monster
  acid_blob - monster
  acid_dragon - monster
  adder - monster
  agate_snail - monster
  agnes - monster
  air_elemental - monster
  aizul - monster
  alligator - monster
  alligator_snapping_turtle - monster
  anaconda - monster
  ancient_bear - monster
  ancient_champion - monster
  ancient_lich - monster
  ancient_zyme - monster
  angel - monster
  ant_larva - monster
  antaeus - monster
  anubis_guard - monster
  apis - monster
  apocalypse_crab - monster
  arachne - monster
  archer_statue - monster
  asmodeus - monster
  asterion - monster
  azrael - monster
  azure_jelly - monster
  baby_alligator - monster
  bai_suzhen - monster
  ball_lightning - monster
  ball_python - monster
  ballistomycete - monster
  ballistomycete_spore - monster
  balrug - monster
  barachi_monster - monster
  basilisk - monster
  bat - monster
  battlesphere - monster
  bennu - monster
  big_fish - monster
  big_kobold - monster
  black_bear - monster
  black_draconian - monster
  black_mamba - monster
  black_sun - monster
  blink_frog - monster
  blizzard_demon - monster
  bloated_husk - monster
  block_of_ice - monster
  blood_saint - monster
  blork_the_orc - monster
  blue_death - monster
  blue_devil - monster
  bog_body - monster
  bog_mummy - monster
  boggart - monster
  bone_dragon - monster
  boring_beetle - monster
  boris - monster
  boulder_beetle - monster
  brain_worm - monster
  briar_patch - monster
  brimstone_fiend - monster
  brown_ooze - monster
  bullfrog - monster
  bumblebee - monster
  bunyip - monster
  burning_bush - monster
  butterfly - monster
  cacodemon - monster
  cane_toad - monster
  catoblepas - monster
  caustic_shrike - monster
  centaur_monster - monster
  centaur_warrior - monster
  cerebov - monster
  chaos_butterfly - monster
  chaos_champion - monster
  chaos_spawn - monster
  charred_statue - monster
  cherub - monster
  chimera - monster
  chuck - monster
  clay_golem - monster
  conjurer_statue - monster
  corrupter - monster
  crawling_corpse - monster
  crazy_yiuf - monster
  crimson_imp - monster
  crocodile - monster
  crystal_golem - monster
  crystal_guardian - monster
  curse_skull - monster
  curse_toe - monster
  cyclops - monster
  daeva - monster
  dancing_weapon - monster
  dart_slug - monster
  death_cob - monster
  death_drake - monster
  death_knight - monster
  death_ooze - monster
  death_scarab - monster
  death_yak - monster
  deathcap - monster
  deep_dwarf_monster - monster
  deep_dwarf_artificer - monster
  deep_dwarf_berserker - monster
  deep_dwarf_death_knight - monster
  deep_dwarf_necromancer - monster
  deep_dwarf_scion - monster
  deep_elf_annihilator - monster
  deep_elf_archer - monster
  deep_elf_blademaster - monster
  deep_elf_conjurer - monster
  deep_elf_death_mage - monster
  deep_elf_demonologist - monster
  deep_elf_elementalist - monster
  deep_elf_fighter - monster
  deep_elf_high_priest - monster
  deep_elf_knight - monster
  deep_elf_mage - monster
  deep_elf_master_archer - monster
  deep_elf_priest - monster
  deep_elf_soldier - monster
  deep_elf_sorcerer - monster
  deep_elf_summoner - monster
  deep_troll - monster
  deep_troll_earth_mage - monster
  deep_troll_shaman - monster
  demigod_monster - monster
  demon - monster
  demonic_crawler - monster
  demonic_monsters - monster
  demonspawn_monster - monster
  derived_undead - monster
  diamond_obelisk - monster
  dire_elephant - monster
  dispater - monster
  dissolution - monster
  donald - monster
  doom_hound - monster
  dowan - monster
  draconian_monster - monster
  draconian_annihilator - monster
  draconian_knight - monster
  draconian_monk - monster
  draconian_scorcher - monster
  draconian_shifter - monster
  draconian_stormcaller - monster
  draconian_zealot - monster
  dream_sheep - monster
  drowned_soul - monster
  dryad - monster
  duane - monster
  duvessa - monster
  dwarf - monster
  earth_elemental - monster
  edmund - monster
  efreet - monster
  eidolon - monster
  eldritch_tentacle - monster
  electric_eel - monster
  electric_golem - monster
  eleionoma - monster
  elemental_wellspring - monster
  elephant - monster
  elephant_slug - monster
  elf - monster
  emperor_scorpion - monster
  entropy_weaver - monster
  ereshkigal - monster
  erica - monster
  erolcha - monster
  ettin - monster
  eustachio - monster
  executioner - monster
  eye_of_devastation - monster
  eye_of_draining - monster
  fannar - monster
  faun - monster
  felid_monster - monster
  fenstrider_witch - monster
  fire_bat - monster
  fire_crab - monster
  fire_dragon - monster
  fire_drake - monster
  fire_elemental - monster
  fire_giant - monster
  fire_vortex - monster
  firespitter_statue - monster
  flaming_corpse - monster
  flayed_ghost - monster
  floating_eye - monster
  flying_skull - monster
  formicid_monster - monster
  formicid_drone - monster
  formicid_venom_mage - monster
  frances - monster
  francis - monster
  frederick - monster
  freezing_wraith - monster
  frilled_lizard - monster
  frost_giant - monster
  frost-covered_statue - monster
  gargoyle_monster - monster
  gastronok - monster
  gelid_demonspawn - monster
  geryon - monster
  ghost_crab - monster
  ghost_moth - monster
  ghoul_monster - monster
  giant_amoeba - monster
  giant_blowfly - monster
  giant_centipede - monster
  giant_cockroach - monster
  giant_firefly - monster
  giant_goldfish - monster
  giant_mite - monster
  giant_slug - monster
  giant_toad - monster
  gila_monster - monster
  gloorx_vloq - monster
  glowing_orange_brain - monster
  glowing_shapeshifter - monster
  gnoll_monster - monster
  gnoll_sergeant - monster
  gnoll_shaman - monster
  goblin - monster
  golden_dragon - monster
  golden_eye - monster
  goliath_beetle - monster
  goliath_frog - monster
  grand_avatar_monster - monster
  great_orb_of_eyes - monster
  green_death - monster
  green_draconian - monster
  grey_draconian - monster
  grey_rat - monster
  griffon - monster
  grinder - monster
  grizzly_bear - monster
  grum - monster
  guardian_golem - monster
  guardian_mummy - monster
  guardian_naga - monster
  guardian_serpent - monster
  hairy_devil - monster
  halazid_warlock - monster
  halfling_monster - monster
  harold - monster
  harpy - monster
  hell_beast - monster
  hell_hog - monster
  hell_hound - monster
  hell_knight - monster
  hell_rat - monster
  hell_sentinel - monster
  hellephant - monster
  hellion - monster
  hellwing - monster
  hill_giant - monster
  hippogriff - monster
  hobgoblin - monster
  hog - monster
  holy_swine - monster
  hornet - monster
  hound - monster
  howler_monkey - monster
  human_monster - monster
  hungry_ghost - monster
  hydra - monster
  ice_beast - monster
  ice_devil - monster
  ice_dragon - monster
  ice_fiend - monster
  ice_statue - monster
  ignacio - monster
  ignis - monster
  iguana - monster
  ijyb - monster
  ilsuiw - monster
  imperial_myrmidon - monster
  inept_mimic - monster
  infernal_demonspawn - monster
  insubstantial_wisp - monster
  iron_devil - monster
  iron_dragon - monster
  iron_elemental - monster
  iron_giant - monster
  iron_golem - monster
  iron_imp - monster
  iron_troll - monster
  ironbrand_convoker - monster
  ironheart_preserver - monster
  jackal - monster
  jelly - monster
  jellyfish - monster
  jessica - monster
  jiangshi - monster
  jorgrun - monster
  jory - monster
  joseph - monster
  josephine - monster
  jozef - monster
  juggernaut - monster
  jumping_spider - monster
  khufu - monster
  killer_bee - monster
  killer_bee_larva - monster
  killer_klown - monster
  kirke - monster
  kobold_monster - monster
  kobold_demonologist - monster
  komodo_dragon - monster
  kraken - monster
  laboratory_rat - monster
  lamia - monster
  large_abomination - monster
  lasher_statue - monster
  lava_fish - monster
  lava_snake - monster
  lava_worm - monster
  lemure - monster
  leopard_gecko - monster
  lich - monster
  lightning_spire - monster
  lindwurm - monster
  list_of_monsters - monster
  lom_lobon - monster
  lorocyproca - monster
  lost_soul - monster
  louise - monster
  lurking_horror - monster
  macabre_mass - monster
  maggie - monster
  mana_viper - monster
  manticore - monster
  mara - monster
  margery - monster
  master_blaster - monster
  master_elementalist - monster
  maud - monster
  maurice - monster
  meliai - monster
  menkaure - monster
  mennas - monster
  merfolk - monster
  merfolk_monster - monster
  merfolk_aquamancer - monster
  merfolk_avatar - monster
  merfolk_impaler - monster
  merfolk_javelineer - monster
  merfolk_siren - monster
  mermaid - monster
  metal_gargoyle - monster
  michael - monster
  midge - monster
  mimic_monster - monster
  minotaur_monster - monster
  mnoleg - monster
  molten_gargoyle - monster
  monster_attributes - monster
  monster_generation - monster
  monsters - monster
  monstrous_demonspawn - monster
  moth_of_suppression - monster
  moth_of_wrath - monster
  mottled_draconian - monster
  mottled_dragon - monster
  mummy_monster - monster
  mummy_priest - monster
  murray - monster
  naga_monster - monster
  naga_mage - monster
  naga_ritualist - monster
  naga_sharpshooter - monster
  naga_warrior - monster
  nagaraja - monster
  nameless_horror - monster
  natasha - monster
  necromancer_monster - monster
  necrophage - monster
  nellie - monster
  neqoxec - monster
  nergalle - monster
  nessos - monster
  nikola - monster
  norbert - monster
  norris - monster
  obsidian_statue - monster
  octopode_monster - monster
  octopode_crusher - monster
  ogre_monster - monster
  ogre_mage - monster
  oklob_plant - monster
  oklob_sapling - monster
  ooze - monster
  ophan - monster
  orange_crystal_statue - monster
  orange_demon - monster
  orb_guardian - monster
  orb_of_fire - monster
  orb_spider - monster
  orc - monster
  orc_high_priest - monster
  orc_knight - monster
  orc_priest - monster
  orc_sorcerer - monster
  orc_warlord - monster
  orc_warrior - monster
  orc_wizard - monster
  paladin_monster - monster
  pale_draconian - monster
  pan_monster - monster
  pandemonium_lord - monster
  peacekeeper - monster
  pearl_dragon - monster
  phantasmal_warrior - monster
  phantom - monster
  phoenix - monster
  pikel - monster
  pillar_of_salt - monster
  pit_fiend - monster
  plague_shambler - monster
  polar_bear - monster
  polymoth - monster
  polyphemus - monster
  porcupine - monster
  priests - monster
  prince_ribbit - monster
  profane_servitor - monster
  psyche - monster
  pulsating_lump - monster
  purgy - monster
  purple_draconian - monster
  putrid_demonspawn - monster
  quasit - monster
  queen_ant - monster
  queen_bee - monster
  quicksilver_dragon - monster
  quokka - monster
  ragged_hierophant - monster
  raiju - monster
  rakshasa - monster
  rat - monster
  raven - monster
  ravenous_mimic - monster
  reaper - monster
  red_devil - monster
  red_draconian - monster
  redback - monster
  revenant - monster
  rime_drake - monster
  river_rat - monster
  robin - monster
  rock_troll - monster
  rock_worm - monster
  rotting_devil - monster
  rotting_hulk - monster
  roxanne - monster
  royal_mummy - monster
  rupert - monster
  rust_devil - monster
  saint_roka - monster
  salamander - monster
  salamander_firebrand - monster
  salamander_mystic - monster
  salamander_stormcaller - monster
  saltling - monster
  satyr - monster
  scorpion - monster
  sea_snake - monster
  seraph - monster
  serpent_of_hell_cocytus - monster
  serpent_of_hell_dis - monster
  serpent_of_hell_gehenna - monster
  serpent_of_hell_tartarus - monster
  servant_of_whispers - monster
  shadow - monster
  shadow_demon - monster
  shadow_dragon - monster
  shadow_imp - monster
  shadow_wraith - monster
  shambling_mangrove - monster
  shapeshifter - monster
  shard_shrike - monster
  shark - monster
  shedu - monster
  sheep - monster
  shining_eye - monster
  shock_serpent - monster
  sigmund - monster
  silent_spectre - monster
  silver_star - monster
  silver_statue - monster
  simulacrum_monster - monster
  sixfirhy - monster
  skeletal_warrior - monster
  skeleton_monster - monster
  sky_beast - monster
  slave - monster
  slime_creature - monster
  small_abomination - monster
  smoke_demon - monster
  snail_statue - monster
  snaplasher_vine - monster
  snapping_turtle - monster
  snorg - monster
  sojobo - monster
  soldier_ant - monster
  sonja - monster
  soul_eater - monster
  spark_wasp - monster
  spatial_maelstrom - monster
  spatial_vortex - monster
  spectral_thing - monster
  spellforged_servitor_monster - monster
  sphinx - monster
  spider - monster
  spiny_worm - monster
  spirit - monster
  spirit_wolf - monster
  spooky_statue - monster
  spriggan_monster - monster
  spriggan_air_mage - monster
  spriggan_assassin - monster
  spriggan_berserker - monster
  spriggan_defender - monster
  spriggan_druid - monster
  spriggan_enchanter - monster
  spriggan_rider - monster
  starcursed_mass - monster
  steam_dragon - monster
  stone_giant - monster
  stone_golem - monster
  storm_dragon - monster
  subtractor_snake - monster
  sun_demon - monster
  swamp_dragon - monster
  swamp_drake - monster
  swamp_worm - monster
  tarantella - monster
  template:monster_info - monster
  tengu_monster - monster
  tengu_conjurer - monster
  tengu_reaver - monster
  tengu_warrior - monster
  tentacled_monstrosity - monster
  tentacled_starspawn - monster
  terence - monster
  terpsichore - monster
  test_spawner - monster
  the_enchantress - monster
  the_iron_giant - monster
  the_lernaean_hydra - monster
  the_royal_jelly - monster
  thorn_hunter - monster
  thorn_lotus - monster
  thrashing_horror - monster
  tiamat - monster
  titan - monster
  toadstool - monster
  toenail_golem - monster
  tormentor - monster
  torpor_snail - monster
  torturous_demonspawn - monster
  training_dummy - monster
  troll - monster
  troll_monster - monster
  twister - monster
  two-headed_ogre - monster
  tyrant_leech - monster
  tzitzimitl - monster
  ufetubus - monster
  ugly_thing - monster
  unborn - monster
  unborn_deep_dwarf - monster
  unseen_horror - monster
  urug - monster
  ushabti - monster
  vampire_monster - monster
  vampire_bat - monster
  vampire_knight - monster
  vampire_mage - monster
  vampire_mosquito - monster
  vapour - monster
  vashnia - monster
  vault_guard - monster
  vault_sentinel - monster
  vault_warden - monster
  very_ugly_thing - monster
  vine_stalker_monster - monster
  viper - monster
  wandering_mushroom - monster
  war_dog - monster
  war_gargoyle - monster
  warg - monster
  warmonger - monster
  wasp - monster
  water_elemental - monster
  water_moccasin - monster
  water_nymph - monster
  white_draconian - monster
  white_imp - monster
  wight - monster
  wiglaf - monster
  will-o-the-wisp - monster
  wind_drake - monster
  wizard_monster - monster
  wizard_statue - monster
  wolf - monster
  wolf_spider - monster
  wood_golem - monster
  worker_ant - monster
  worldbinder - monster
  worm - monster
  wraith - monster
  wretched_star - monster
  wyvern - monster
  xtahua - monster
  yak - monster
  yaktaur - monster
  yaktaur_captain - monster
  yellow_draconian - monster
  ynoxinul - monster
  zombie - monster
  zot_statue - monster


  agile_status - status_effect
  antimagic_status - status_effect
  augmentation_status - status_effect
  bad_forms_status - status_effect
  berserk_status - status_effect
  black_mark_status - status_effect
  blind_status - status_effect
  brilliant_status - status_effect
  charm_status - status_effect
  confusing_touch_status - status_effect
  confusion_status - status_effect
  constriction_status - status_effect
  cooldowns_status - status_effect
  corona_status - status_effect
  corrosion_status - status_effect
  darkness_status - status_effect
  dazed_status - status_effect
  death_channel_status - status_effect
  deaths_door_status - status_effect
  deflect_missiles_status - status_effect
  disjunction_status - status_effect
  divine_protection_status - status_effect
  divine_shield_status - status_effect
  doom_howl_status - status_effect
  drain_status - status_effect
  engorged_status - status_effect
  engulf_status - status_effect
  fast_slow_status - status_effect
  fear_status - status_effect
  finesse_status - status_effect
  fire_vulnerable_status - status_effect
  flayed_status - status_effect
  flight_status - status_effect
  frozen_status - status_effect
  haste_status - status_effect
  heavenly_storm_status - status_effect
  held_status - status_effect
  heroism_status - status_effect
  horrified_status - status_effect
  inner_flame_status - status_effect
  invisibility_status - status_effect
  in_lava_status - status_effect
  ledas_liquefaction_status - status_effect
  magic_contamination_status - status_effect
  mark_status - status_effect
  mesmerised_status - status_effect
  might_status - status_effect
  mirror_damage_status - status_effect
  no_potions_status - status_effect
  no_scrolls_status - status_effect
  olgrebs_toxic_radiance_status - status_effect
  orb_status - status_effect
  ozocubus_armour_status - status_effect
  paralysis_status - status_effect
  petrifying_or_petrified_status - status_effect
  poison_status - status_effect
  powered_by_death_status - status_effect
  quad_damage_status - status_effect
  recall_status - status_effect
  regenerating_status - status_effect
  repel_missiles_status - status_effect
  resistance_status_effect_status - status_effect
  ring_of_flames_status - status_effect
  sapped_magic_status - status_effect
  scrying_status - status_effect
  searing_ray_status - status_effect
  serpents_lash_status - status_effect
  shroud_of_golubria_status - status_effect
  sickness_status - status_effect
  silence_status - status_effect
  sleep_status - status_effect
  slimify_status - status_effect
  slow_status - status_effect
  sluggish_status - status_effect
  starving_status - status_effect
  stat_zero_status - status_effect
  sticky_flame_status - status_effect
  still_winds_status - status_effect
  swiftness_status - status_effect
  teleport_status - status_effect
  teleport_prevention_status - status_effect
  tornado_status - status_effect
  transmutations_status - status_effect
  umbra_status - status_effect
  vitalisation_status - status_effect
  vulnerable_status - status_effect
  water_status - status_effect
  weak_status - status_effect

  acute_vision - mutation
  antennae - mutation
  beak - mutation
  big_wings - mutation
  blink - mutation
  camouflage - mutation
  clarity - mutation
  claws - mutation
  cold_resistance - mutation
  electricity_resistance - mutation
  evolution - mutation
  fangs - mutation
  fire_resistance - mutation
  high_mp - mutation
  hooves - mutation
  horns - mutation
  icy_blue_scales - mutation
  improved_attributes - mutation
  iridescent_scales - mutation
  large_bone_plates - mutation
  magic_resistance - mutation
  molten_scales - mutation
  mutation_resistance - mutation
  passive_mapping - mutation
  poison_breath - mutation
  poison_resistance - mutation
  regeneration - mutation
  repulsion_field - mutation
  robust - mutation
  rugged_brown_scales - mutation
  shaggy_fur - mutation
  slimy_green_scales - mutation
  stinger - mutation
  strong_legs - mutation
  talons - mutation
  tentacle_spike - mutation
  thin_metallic_scales - mutation
  thin_skeletal_structure - mutation
  tough_skin - mutation
  wild_magic - mutation
  yellow_scales - mutation

  ashenzari - god
  beogh - god
  cheibriados - god
  dithmenos - god
  elyvilon - god
  fedhas - god
  gozag - god
  hepliaklqana - god
  jiyva - god
  kikubaaqudgha - god
  lugonu - god
  makhleb - god
  nemelex - god
  okawaru - god
  qazlal - god
  ru - god
  sif - god
  trog - god
  uskayaw - god
  vehumet - god
  wu_jian - god
  xom - god
  yredelemnul - god
  zin - god
  shining_one - god

  unknown - god

  ambrosia_potion - potion
  berserkrage_potion - potion
  brilliance_potion - potion
  cancellation_potion - potion
  curing_potion - potion
  degeneration_potion - potion
  experience_potion - potion
  flight_potion - potion
  haste_potion - potion
  healwounds_potion - potion
  invisibility_potion - potion
  lignification_potion - potion
  magic_potion - potion
  might_potion - potion
  mutation_potion - potion
  resistance_potion - potion
  stabbing_potion - potion

  acquirement_scroll - scroll
  amnesia_scroll - scroll
  blinking_scroll - scroll
  brandweapon_scroll - scroll
  enchantarmour_scroll - scroll
  enchantweapon_scroll - scroll
  fear_scroll - scroll
  fog_scroll - scroll
  holyword_scroll - scroll
  identity_scroll - scroll
  immolation_scroll - scroll
  magicmapping_scroll - scroll
  noise_scroll - scroll
  randomuselessness_scroll - scroll
  removecurse_scroll - scroll
  silence_scroll - scroll
  summoning_scroll - scroll
  teleportation_scroll - scroll
  torment_scroll - scroll
  vulnerability_scroll - scroll

  alistairs_intoxication_spell - non_target_based_spell
  animate_dead_spell - non_target_based_spell
  animate_skeleton_spell - non_target_based_spell
  aura_of_abjuration_spell - non_target_based_spell
  beastly_appendage_spell - non_target_based_spell
  blade_hands_spell - non_target_based_spell
  blink_spell - non_target_based_spell
  borgnjors_revivification_spell - non_target_based_spell
  call_canine_familiar_spell - non_target_based_spell
  call_imp_spell - non_target_based_spell
  chain_lightning_spell - non_target_based_spell
  confusing_touch_spell - non_target_based_spell
  conjure_ball_lightning_spell - non_target_based_spell
  conjure_flame_spell - non_target_based_spell
  controlled_blink_spell - non_target_based_spell
  corpse_rot_spell - non_target_based_spell
  death_channel_spell - non_target_based_spell
  deaths_door_spell - non_target_based_spell
  discord_spell - non_target_based_spell
  disjunction_spell - non_target_based_spell
  dragon_form_spell - non_target_based_spell
  dragons_call_spell - non_target_based_spell
  eringyas_noxious_bog_spell - non_target_based_spell
  excruciating_wounds_spell - non_target_based_spell
  foxfire_spell - non_target_based_spell
  hydra_form_spell - non_target_based_spell
  ice_form_spell - non_target_based_spell
  ignite_poison_spell - non_target_based_spell
  ignition_spell - non_target_based_spell
  infusion_spell - non_target_based_spell
  iskenderuns_battlesphere_spell - non_target_based_spell
  ledas_liquefaction_spell - non_target_based_spell
  malign_gateway_spell - non_target_based_spell
  metabolic_englaciation_spell - non_target_based_spell
  monstrous_menagerie_spell - non_target_based_spell
  necromutation_spell - non_target_based_spell
  olgrebs_toxic_radiance_spell - non_target_based_spell
  ozocubus_armour_spell - non_target_based_spell
  ozocubus_refrigeration_spell - non_target_based_spell
  portal_projectile_spell - non_target_based_spell
  recall_spell - non_target_based_spell
  ring_of_flames_spell - non_target_based_spell
  shadow_creatures_spell - non_target_based_spell
  shatter_spell - non_target_based_spell
  shroud_of_golubria_spell - non_target_based_spell
  silence_spell_spell - non_target_based_spell
  simulacrum_spell - non_target_based_spell
  song_of_slaying_spell - non_target_based_spell
  spectral_weapon_spell - non_target_based_spell
  spellforged_servitor_spell - non_target_based_spell
  spider_form_spell - non_target_based_spell
  statue_form_spell - non_target_based_spell
  sticks_to_snakes_spell - non_target_based_spell
  sublimation_of_blood_spell - non_target_based_spell
  summon_demon_spell - non_target_based_spell
  summon_forest_spell - non_target_based_spell
  summon_greater_demon_spell - non_target_based_spell
  summon_guardian_golem_spell - non_target_based_spell
  summon_horrible_things_spell - non_target_based_spell
  summon_hydra_spell - non_target_based_spell
  summon_ice_beast_spell - non_target_based_spell
  summon_mana_viper_spell - non_target_based_spell
  summon_small_mammal_spell - non_target_based_spell
  swiftness_spell - non_target_based_spell
  absolute_zero_spell - target_based_spell
  agony_spell - target_based_spell
  airstrike_spell - target_based_spell
  apportation_spell - target_based_spell
  bolt_of_magma_spell - target_based_spell
  borgnjors_vile_clutch_spell - target_based_spell
  cause_fear_spell - target_based_spell
  corona_spell - target_based_spell
  dazzling_flash_spell - target_based_spell
  dispel_undead_spell - target_based_spell
  dispersal_spell - target_based_spell
  ensorcelled_hibernation_spell - target_based_spell
  fire_storm_spell - target_based_spell
  fireball_spell - target_based_spell
  freeze_spell - target_based_spell
  freezing_cloud_spell - target_based_spell
  frozen_ramparts_spell - target_based_spell
  fulminant_prism_spell - target_based_spell
  gells_gravitas_spell - target_based_spell
  hailstorm_spell - target_based_spell
  haunt_spell - target_based_spell
  infestation_spell - target_based_spell
  inner_flame_spell - target_based_spell
  invisibility_spell_spell - target_based_spell
  iron_shot_spell - target_based_spell
  irradiate_spell - target_based_spell
  iskenderuns_mystic_blast_spell - target_based_spell
  lees_rapid_deconstruction_spell - target_based_spell
  lehudibs_crystal_spear_spell - target_based_spell
  lesser_beckoning_spell - target_based_spell
  lightning_bolt_spell - target_based_spell
  magic_dart_spell - target_based_spell
  mephitic_cloud_spell - target_based_spell
  orb_of_destruction_spell - target_based_spell
  pain_spell - target_based_spell
  passage_of_golubria_spell - target_based_spell
  passwall_spell - target_based_spell
  petrify_spell - target_based_spell
  poisonous_vapours_spell - target_based_spell
  sandblast_spell - target_based_spell
  searing_ray_spell - target_based_spell
  shock_spell - target_based_spell
  slow_spell - target_based_spell
  starburst_spell - target_based_spell
  static_discharge_spell - target_based_spell
  sticky_flame_spell - target_based_spell
  sting_spell - target_based_spell
  stone_arrow_spell - target_based_spell
  summon_lightning_spire_spell - target_based_spell
  teleport_other_spell - target_based_spell
  tornado_spell - target_based_spell
  tukimas_dance_spell - target_based_spell
  vampiric_draining_spell - target_based_spell
  yaras_violent_unravelling_spell - target_based_spell

  fighting - skill
  long_blades - skill
  short_blades - skill
  axes - skill
  maces_&_flails - skill
  polearms - skill
  staves - skill
  unarmed_combat - skill
  bows - skill
  crossbows - skill
  throwing - skill
  slings - skill
  armour - skill
  dodging - skill
  shields - skill
  spellcasting - skill
  conjurations - skill
  hexes - skill
  charms - skill
  summonings - skill
  necromancy - skill
  translocations - skill
  transmutation - skill
  fire_magic - skill
  ice_magic - skill
  air_magic - skill
  earth_magic - skill
  poison_magic - skill
  invocations - skill
  evocations - skill
  stealth - skill

  apocalypse_ability - non_target_ability
  banish_self_ability - non_target_ability
  bat_form_ability - non_target_ability
  bend_space_ability - non_target_ability
  bend_time_ability - non_target_ability
  berserk_ability - non_target_ability
  blink_ability - non_target_ability
  briar_patch_ability - non_target_ability
  bribe_branch_ability - non_target_ability
  brothers_in_arms_ability - non_target_ability
  call_merchant_ability - non_target_ability
  channel_magic_ability - non_target_ability
  cleansing_flame_ability - non_target_ability
  corrupt_ability - non_target_ability
  cure_bad_mutations_ability - non_target_ability
  depart_abyss_ability - non_target_ability
  disaster_area_ability - non_target_ability
  divine_protection_ability - non_target_ability
  divine_shield_ability - non_target_ability
  divine_vigour_ability - non_target_ability
  drain_life_ability - non_target_ability
  draw_out_power_ability - non_target_ability
  elemental_force_ability - non_target_ability
  finesse_ability - non_target_ability
  flight_ability_ability - non_target_ability
  gain_random_mutations_ability - non_target_ability
  greater_healing_ability - non_target_ability
  grow_ballistomycete_ability - non_target_ability
  grow_oklob_plant_ability - non_target_ability
  heal_wounds_ability - non_target_ability
  heavenly_storm_ability - non_target_ability
  heroism_ability - non_target_ability
  idealise_ability - non_target_ability
  lesser_healing_ability - non_target_ability
  purification_ability - non_target_ability
  recall_ability - non_target_ability
  recall_undead_slaves_ability - non_target_ability
  receive_corpses_ability - non_target_ability
  receive_necronomicon_ability - non_target_ability
  recite_ability - non_target_ability
  request_jelly_ability - non_target_ability
  resurrection_ability - non_target_ability
  sanctuary_ability - non_target_ability
  scrying_ability - non_target_ability
  serpents_lash_ability - non_target_ability
  shadow_form_ability - non_target_ability
  slimify_ability - non_target_ability
  slouch_ability - non_target_ability
  step_from_time_ability - non_target_ability
  stomp_ability - non_target_ability
  summon_divine_warrior_ability - non_target_ability
  summon_greater_servant_ability - non_target_ability
  summon_lesser_servant_ability - non_target_ability
  temporal_distortion_ability - non_target_ability
  toggle_divine_energy_ability - non_target_ability
  toggle_injury_mirror_ability - non_target_ability
  torment_ability - non_target_ability
  trogs_hand_ability - non_target_ability
  vitalisation_ability - non_target_ability
  wall_jump_ability - non_target_ability
  animate_dead - target_ability_location
  animate_remains - target_ability_location
  banish - target_ability_location
  controlled_blink - target_ability_location
  enslave_soul - target_ability_location
  give_item_to_follower - target_ability_location
  grand_finale - target_ability_location
  heal_other - target_ability_location
  hop - target_ability_location
  Imprison - target_ability_location
  line_pass - target_ability_location
  major_destruction - target_ability_location
  minor_destruction - target_ability_location
  overgrow - target_ability_location
  power_leap - target_ability_location
  rolling_charge - target_ability_location
  shadow_step - target_ability_location
  smite - target_ability_location
  spit_poison - target_ability_location
  transference - target_ability_location
  upheaval - target_ability_location
  ancestor_identity - target_ability_menu
  ancestor_life - target_ability_menu
  brand_weapon_with_holy - target_ability_menu
  brand_weapon_with_pain - target_ability_menu
  corrupt_weapon - target_ability_menu
  curse_item - target_ability_menu
  deal_four - target_ability_menu
  forget_spell - target_ability_menu
  pick_a_card_any_card - target_ability_menu
  stack_five - target_ability_menu
  transfer_knowledge - target_ability_menu
  triple_draw - target_ability_menu
  potion_petition - target_ability_text_message

  dungeon_1 - place
  dungeon_2 - place
  dungeon_3 - place
  dungeon_4 - place
  dungeon_5 - place
  dungeon_6 - place
  dungeon_7 - place
  dungeon_8 - place
  dungeon_9 - place
  dungeon_10 - place
  dungeon_11 - place
  dungeon_12 - place
  dungeon_13 - place
  dungeon_14 - place
  dungeon_15 - place

  lair_1 - place
  lair_2 - place
  lair_3 - place
  lair_4 - place
  lair_5 - place
  lair_6 - place

  swamp_1 - place
  swamp_2 - place
  swamp_3 - place
  swamp_4 - place

  shoals_1 - place
  shoals_2 - place
  shoals_3 - place
  shoals_4 - place

  snake_pit_1 - place
  snake_pit_2 - place
  snake_pit_3 - place
  snake_pit_4 - place

  spiders_nest_1 - place
  spiders_nest_2 - place
  spiders_nest_3 - place
  spiders_nest_4 - place

  slime_pits_1 - place
  slime_pits_2 - place
  slime_pits_3 - place
  slime_pits_4 - place
  slime_pits_5 - place

  orcish_mines_1 - place
  orcish_mines_2 - place

  elven_halls_1 - place
  elven_halls_2 - place
  elven_halls_3 - place

  vaults_1 - place
  vaults_2 - place
  vaults_3 - place
  vaults_4 - place
  vaults_5 - place

  crypt_1 - place
  crypt_2 - place
  crypt_3 - place

  tomb_1 - place
  tomb_2 - place
  tomb_3 - place

  depths_1 - place
  depths_2 - place
  depths_3 - place
  depths_4 - place
  depths_5 - place

  abyss_1 - place
  abyss_2 - place
  abyss_3 - place
  abyss_4 - place
  abyss_5 - place

  cocytus_1 - place
  cocytus_2 - place
  cocytus_3 - place
  cocytus_4 - place
  cocytus_5 - place
  cocytus_6 - place
  cocytus_7 - place

  gehenna_1 - place
  gehenna_2 - place
  gehenna_3 - place
  gehenna_4 - place
  gehenna_5 - place
  gehenna_6 - place
  gehenna_7 - place

  tartarus_1 - place
  tartarus_2 - place
  tartarus_3 - place
  tartarus_4 - place
  tartarus_5 - place
  tartarus_6 - place
  tartarus_7 - place

  iron_city_of_dis_1 - place
  iron_city_of_dis_2 - place
  iron_city_of_dis_3 - place
  iron_city_of_dis_4 - place
  iron_city_of_dis_5 - place
  iron_city_of_dis_6 - place
  iron_city_of_dis_7 - place

  zot_1 - place
  zot_2 - place
  zot_3 - place
  zot_4 - place
  zot_5 - place

) ;; end constants


(:predicates
    ; N,S,E,W,NE,NW,SE,SW of a cell
    (northof ?cell1 ?cell2 - cell) ; ?cell2 is north of ?cell1
    (southof ?cell1 ?cell2 - cell)
    (eastof ?cell1 ?cell2 - cell)
    (westof ?cell1 ?cell2 - cell)
    (northeastof ?cell1 ?cell2 - cell)
    (northwestof ?cell1 ?cell2 - cell)
    (southeastof ?cell1 ?cell2 - cell)
    (southwestof ?cell1 ?cell2 - cell)

    (opendoor ?cell - cell)
    (closeddoor ?cell - cell)

    (statue ?cell - cell)

    (hasterrain ?cell - cell ?terrain - terrain)

    ;altars enable worshipping a god
    (altarat ?cell - cell ?god - god)
    ; player god
    (player_worshipping ?god - god)
    (player_piety ?amount - qualitative_quantity)

    ; player loc
    (playerat ?cell - cell)

    ; player health
    (playerhealth ?amount - qualitative_quantity)

    ; monster related predicates - only one monster per cell
    (hasmonster ?cell - cell)
    (monster_danger_rating ?cell - cell ?danger - danger_rating)
    (monster_health ?cell - cell ?amount - qualitative_quantity)
    (monster_status_effect ?cell - cell ?status - status_effect)

    ; levels
    (playerplace ?place - place)
    (deeper ?place_above ?place_below - place)
    (connected ?currentplace ?nextlowestplace - place)
    (hasstairsdown ?cell - cell)
    (hasstairsup ?cell - cell)

    ; items
    (haspotion ?cell - cell)
    (hasscroll ?cell - cell)
    (hasweapon ?cell - cell)
    (hasarmour ?cell - cell)
    (hasfooditem ?cell - cell)
    (hasitem ?cell - cell ?item - item)

    ; special items
    (hasorbofzot ?cell - cell)
    (hasrune ?rune - rune ?cell - cell)

    ; special items that do not take up inventory space
    (playerhasorbofzot)
    (playerhasrune ?rune - rune)

    ; inventory
    (invhaspotion ?potion - potion)
    (invhasscroll ?scroll - scroll)
    (invhasarmour ?armour - armour)
    (invhasweapon ?weapon - weapon)
    (invhasitem ?item - item)

    ; what is equipped on the player
    (equippedarmour ?armour - armour)
    (equippedweapon ?weapon - weapon)

    ; placeholders for the effects of potions and scrolls
    ; these placeholders signify that the potion has some effect on the player
    ; and is useful when the player's goal is to consume an unidentified
    ; potion or scroll, usually in an attempt to either (1) identify the item or
    ; (2) because they are in a dire situation and are desparate for any help
    (has_generic_potion_effect ?potion - potion)
    (has_generic_scroll_effect ?scroll - scroll)
    (has_generic_spell_effect ?spell - spell)
    (has_generic_ability_effect ?ability - ability)

    ; skills are how the player allocates experience levels
    (training_off ?skill - skill)
    (training_low ?skill - skill)
    (training_high ?skill - skill)
    (player_skill_level ?skill - skill ?amount - qualitative_quantity)

    ; spells
    (player_memorised_spell ?spell - spell)
    (spell_chance_of_failure ?spell - spell ?amount - qualitative_quantity)
    (spell_available_to_memorise ?spell - spell)

    ;abilities
    (player_has_ability ?ability - ability)
    (ability_chance_of_failure ?ability - ability ?amount - qualitative_quantity)
)


(:action move_or_attack_s
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_n
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)


(:action move_or_attack_e
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (eastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_w
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (westof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_nw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northwestof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_sw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southwestof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_ne
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northeastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_se
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southeastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action open-door-n
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-s
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-e
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (eastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-w
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (westof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-nw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northwestof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-sw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southwestof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-ne
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northeastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-se
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southeastof ?currcell ?destcell)
        (not (hasterrain ?destcell stone_wall))
        (not (statue ?destcell))
        (not (hasterrain ?destcell lava))
        (not (hasterrain ?destcell plant))
        (not (hasterrain ?destcell trees))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action attack_without_move_n
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_s
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_s
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_e
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (eastof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_w
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (westof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_ne
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northeastof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_nw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (northwestof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_se
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southeastof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action attack_without_move_sw
    :parameters (?currcell ?destcell - cell)
    :precondition
    (and
        (southwestof ?currcell ?destcell)
        (hasmonster ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (hasmonster ?destcell))
    )
)

(:action rest_and_long_wait
    :parameters ()
    :precondition
    (and
        (not (playerhealth maxed))
    )
    :effect
    (and
        (playerhealth maxed)
    )
)

(:action travel_staircase_down
    :parameters (?currentplace - place ?currcell - cell ?nextlowestplace - place)
    :precondition
    (and
        (playerat ?currcell)
        (hasstairsdown ?currcell)
        (playerplace ?currentplace)
        (connected ?currentplace ?nextlowestplace)
    )
    :effect
    (and
        (not (playerplace ?currentplace))
        (playerplace ?nextlowestplace)
    )
)

(:action travel_staircase_up
    :parameters (?currentplace - place ?currcell - cell ?nexthighestplace - place)
    :precondition
    (and
        (playerat ?currcell)
        (hasstairsup ?currcell)
        (playerplace ?currentplace)
        (connected ?nexthighestplace ?currentplace)
    )
    :effect
    (and
        (not (playerplace ?currentplace))
        (playerplace ?nexthighestplace)
    )
)


(:action pickup_item
    :parameters (?item - item ?cell - cell)
    :precondition
    (and
        (playerat ?cell)
        (hasitem ?cell ?item)
    )
    :effect
    (and
        (invhasitem ?item)
    )
)

(:action drop_item
    :parameters (?item - item ?cell - cell)
    :precondition
    (and
        (playerat ?cell)
        (invhasitem ?item)
    )
    :effect
    (and
        (hasitem ?cell ?item)
    )
)


(:action equip_weapon
    :parameters (?weaponitem - weapon)
    :precondition
    (and
        (invhasweapon ?weaponitem)
        (not (equippedweapon ?weaponitem))
    )
    :effect
    (and
        (equippedweapon ?weaponitem)
    )
)


(:action equip_armour
    :parameters (?armouritem - armour)
    :precondition
    (and
        (invhasarmour ?armouritem)
        (not (equippedarmour ?armouritem))
    )
    :effect
    (and
        (equippedarmour ?armouritem)
    )
)

(:action remove_weapon
    :parameters (?weaponitem - weapon)
    :precondition
    (and
        (invhasweapon ?weaponitem)
        (equippedweapon ?weaponitem)
    )
    :effect
    (and
        (not (equippedweapon ?weaponitem))
    )
)


(:action remove_armour
    :parameters (?armouritem - armour)
    :precondition
    (and
        (invhasarmour ?armouritem)
        (equippedarmour ?armouritem)
    )
    :effect
    (and
        (not (equippedarmour ?armouritem))
    )
)


(:action consume_potion
    :parameters (?potion - potion)
    :precondition
    (and
        (invhaspotion ?potion)
    )
    :effect
    (and
        (has_generic_potion_effect ?potion)
    )
)

(:action consume_scroll
    :parameters (?scroll - scroll)
    :precondition
    (and
        (invhasscroll ?scroll)
    )
    :effect
    (and
        (has_generic_scroll_effect ?scroll)
    )
)

(:action attack_by_throwing
    :parameters (?item - item ?targetcell - cell)
    :precondition
    (and
        (invhasitem ?item)
    )
    :effect
    (and
        (not (hasmonster ?targetcell))
    )
)


(:action stop_training_skill
    :parameters (?skill - skill)
    :precondition
    (and
        (not (training_off ?skill))
        (or (training_low ?skill) (training_high ?skill))
    )
    :effect
    (and
        (training_off ?skill)
        (not (training_low ?skill))
        (not (training_high ?skill))
    )
)

(:action train_skill_low
    :parameters (?skill - skill)
    :precondition
    (and
        (not (training_low ?skill))
        (or (training_off ?skill) (training_high ?skill))
    )
    :effect
    (and
        (not (training_off ?skill))
        (training_low ?skill)
        (not (training_high ?skill))
    )
)

(:action train_skill_high
    :parameters (?skill - skill)
    :precondition
    (and
        (not (training_high ?skill))
        (or (training_off ?skill) (training_low ?skill))
    )
    :effect
    (and
        (not (training_off ?skill))
        (not (training_low ?skill))
        (training_high ?skill)
    )
)


(:action cast_spell_on_target
    :parameters (?spell - target_based_spell ?cell - cell)
    :precondition
    (and
        (player_memorised_spell ?spell)
        (hasmonster ?cell)
    )
    :effect
    (and
        (not (hasmonster ?cell))
    )
)

(:action cast_non_target_spell
    :parameters (?spell - non_target_based_spell)
    :precondition
    (and
        (player_memorised_spell ?spell)
    )
    :effect
    (and
        (has_generic_spell_effect ?spell)
    )
)

(:action use_non_target_ability
    :parameters (?ability - non_target_ability)
    :precondition
    (and
        (player_has_ability ?ability)
    )
    :effect
    (and
        (has_generic_ability_effect ?ability)
    )
)

(:action use_target_location_ability
    :parameters (?ability - target_ability_location ?cell - cell)
    :precondition
    (and
        (player_has_ability ?ability)
    )
    :effect
    (and
        (has_generic_ability_effect ?ability)
    )
)

(:action use_target_based_ability
    :parameters (?ability - target_ability_location)
    :precondition
    (and
        (player_has_ability ?ability)
    )
    :effect
    (and
        (has_generic_ability_effect ?ability)
    )
)


(:action worship_altar
    :parameters (?cell - cell ?god - god)
    :precondition
    (and
        (playerat ?cell)
        (altarat ?cell ?god)
    )
    :effect
    (and
        (player_worshipping ?god)
    )
)


)
