(define (domain dcss)
(:requirements :strips :negative-preconditions)
(:predicates
    ; N,S,E,W,NE,NW,SE,SW of a cell
    (northof ?cell1 ?cell2) ; ?cell2 is north of ?cell1
    (southof ?cell1 ?cell2)
    (eastof ?cell1 ?cell2)
    (westof ?cell1 ?cell2)
    (northeastof ?cell1 ?cell2)
    (northwestof ?cell1 ?cell2)
    (southeastof ?cell1 ?cell2)
    (southwestof ?cell1 ?cell2)
    ; wall
    (wall ?cell)
    ; closed door
    (closeddoor ?cell)
    ; statue is basically like a wall
    (statue ?cell)
    ; lava is like a wall in that it should be avoided
    (lava ?cell)
    ; plant is like a wall in that it should be avoided
    (plant ?cell)
    ; player loc
    (playerat ?cell)
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (not (closeddoor ?destcell))
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
        (closeddoor ?destcell)
        (playerat ?currcell)
    )
    :effect
    (and
        (not (closeddoor ?destcell))
    )
)

)



