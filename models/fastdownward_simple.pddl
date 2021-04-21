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
;;;
;;;     2. Quantities of items, such as potions, etc. are not represented
;;;        because this domain model does not support integers.


(define (domain dcss)
(:requirements :strips :negative-preconditions :existential-preconditions)
(:types monster
        cell
        place ; examples: zot_4, dungeon_12, vaults_2
        skill
        ability
        spell
        god
        qualitative_quantity
        status
        mutation
        terrain
        danger_rating

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
    (monster_status_effect ?cell - cell ?status - status)

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

(:action move_or_attack_n
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_s
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_e
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (eastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_w
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (westof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_nw
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northwestof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_sw
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southwestof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_ne
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northeastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action move_or_attack_se
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southeastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (playerat ?currcell)
    )
    :effect
    (and
        (playerat ?destcell)
        (not (playerat ?currcell))
    )
)

(:action open-door-n
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-s
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-e
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (eastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-w
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (westof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-nw
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northwestof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-sw
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southwestof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-ne
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (northeastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action open-door-se
    :parameters (?currcell ?destcell)
    :precondition
    (and
        (southeastof ?currcell ?destcell)
        (not (wall ?destcell))
        (not (statue ?destcell))
        (not (lava ?destcell))
        (not (plant ?destcell))
        (not (tree ?destcell))
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

(:action attack_without_move_n
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
    :parameters (?currcell ?destcell)
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
        (playerlessthanfullhealth)
    )
    :effect
    (and
        (playerfullhealth)
    )
)

(:action travel_staircase_down
    :parameters (?currentplace ?currcell ?nextlowestplace)
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
    :parameters (?currentplace ?currcell ?nexthighestplace)
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
        (playerplace ?nextlowestplace)
    )
)


(:action pickup_item
    :parameters (?item ?cell)
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
    :parameters (?item ?cell)
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
    :parameters (?weaponitem)
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
    :parameters (?armouritem)
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
    :parameters (?weaponitem)
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
    :parameters (?armouritem)
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
    :parameters (?potion)
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
    :parameters (?scroll)
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
    :parameters (?item ?targetcell)
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
