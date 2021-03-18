(define (domain dcss)
(:requirements :strips :negative-preconditions :existential-preconditions :adl :derived-predicates)
(:types monster
        cell
        place ; examples: zot_4, dungeon_12, vaults_2

        consumeitem - item
        equipitem - item
        potion - consumeitem
        scroll - consumeitem
        fooditem - consumeitem
        weapon - equipitem
        armour - equipitem

        ambrosiapot - potion
        berserkragepot - potion
        brilliancepot - potion
        cancellationpot - potion
        curingpot - potion
        degenerationpot - potion
        experiencepot - potion
        flightpot - potion
        hastepot - potion
        healwoundspot - potion
        invisibilitypot - potion
        lignificationpot - potion
        magicpot - potion
        mightpot - potion
        mutationpot - potion
        resistancepot - potion
        stabbingpot - potion

        acquirementscroll - scroll
        amnesiascroll - scroll
        blinkingscroll - scroll
        brandweaponscroll - scroll
        enchantarmourscroll - scroll
        enchantweaponscroll - scroll
        fearscroll - scroll
        fogscroll - scroll
        holywordscroll - scroll
        identityscroll - scroll
        immolationscroll - scroll
        magicmappingscroll - scroll
        noisescroll - scroll
        randomuselessnessscroll - scroll
        removecursescroll - scroll
        silencescroll - scroll
        summoningscroll - scroll
        teleportationscroll - scroll
        tormentscroll - scroll
        vulnerabilityscroll - scroll

        hungerlevel
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
    ; wall
    (wall ?cell - cell)
    ; closed door
    (closeddoor ?cell - cell)
    ; statue is basically like a wall
    (statue ?cell - cell)
    ; lava is like a wall in that it should be avoided
    (lava ?cell - cell)
    ; plant is like a wall in that it should be avoided
    (plant ?cell - cell)
    ; tree is like a wall in that it should be avoided
    (tree ?cell - cell)
    ; player loc
    (playerat ?cell - cell)
    ; player health
    (playerlessthanfullhealth)
    (playerfullhealth)
    ; has monster if there is a monster at that cell
    (hasmonster ?cell - cell)
    ; levels
    (playerplace ?place - place)
    (deeper ?place_above ?place_below - place)
    (connected ?currentplace ?nextlowestplace - place)
    (hasstairsdown ?cell - cell)
    ; items
    (haspotion ?cell - cell)
    (hasscroll ?cell - cell)
    (hasweapon ?cell - cell)
    (hasarmour ?cell - cell)
    (hasfooditem ?cell - cell)

    ; hunger
    (playerhashunger ?hunger - hungerlevel)

    ; inventory
    (invhaspotion ?potion - potion)
    (invhasscroll ?scroll - scroll)
    (invhasarmour ?armour - armour)
    (invhasweapon ?weapon - weapon)
    (invhasfooditem ?food - fooditem)

    ; what is equipped on the player
    (equippedarmour ?armour - armour)
    (equippedweapon ?weapon - weapon)
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

(:action rest_and_long_wait
    :parameters ()
    :precondition
    (and (playerlessthanfullhealth))
    :effect
    (and (playerfullhealth))
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


(:action eat
    :parameters (?food)
    :precondition
    (and
        (invhasfooditem ?food)
        (or (playerhashunger fainting) (playerhashunger starving) (playerhashunger nearstarving) (playerhashunger hungry))
    )
    :effect
    (and
        (or (playerhashunger full) (playerhashunger veryfull) (playerhashunger engorged))
    )
)

; (:action pickupitems...
; (:action equipitems...
; (:action consumepotion healwounds ...
; (:action consumescroll remove curse...


)


