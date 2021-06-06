from enum import Enum


class AuxiliaryAttack(Enum):

    """
    Represents an auxiliary attack that an agent has. See http://crawl.chaosforge.org/Auxiliary_attack
    """

    OFFHAND_PUNCH = 1
    OFFHAND_PUNCH_W_CLAWS = 2
    OFFHAND_PUNCH_W__BLADE_HANDS = 3
    HEADBUTT = 4
    PECK = 5
    KICK_W_HOOVES = 6
    KICK_W_TALONS = 7
    TAIL_SLAP = 8
    TAIL_SLAP_W_STINGER = 9
    BITE_W_FANGS = 10
    BITE_W_ACIDIC_BITE = 11
    BITE_W_ANTI_MAGIC_BITE = 12
    PSEUDOPODS = 13
    TENTACLE_SPIKE = 14
    TENTACLE_SLAP = 15
    TENTACLES_SQUEEZE = 16
    CONSTRICTION = 17


class AuxiliaryAttackMapping:

    """
    Assists parsing what auxiliary attack the player has from websocket data
    """

    auxiliary_attack_menu_messages_lookup = {

    "": AuxiliaryAttack.OFFHAND_PUNCH,
    "": AuxiliaryAttack.OFFHAND_PUNCH_W_CLAWS,
    "": AuxiliaryAttack.OFFHAND_PUNCH_W__BLADE_HANDS,
    "You reflexively headbutt those who attack you in melee": AuxiliaryAttack.HEADBUTT,
    "": AuxiliaryAttack.PECK,
    "": AuxiliaryAttack.KICK_W_HOOVES,
    "": AuxiliaryAttack.KICK_W_TALONS,
    "": AuxiliaryAttack.TAIL_SLAP,
    "": AuxiliaryAttack.TAIL_SLAP_W_STINGER,
    "": AuxiliaryAttack.BITE_W_FANGS,
    "": AuxiliaryAttack.BITE_W_ACIDIC_BITE,
    "": AuxiliaryAttack.BITE_W_ANTI_MAGIC_BITE,
    "": AuxiliaryAttack.PSEUDOPODS,
    "": AuxiliaryAttack.TENTACLE_SPIKE,
    "": AuxiliaryAttack.TENTACLE_SLAP,
    "": AuxiliaryAttack.TENTACLES_SQUEEZE,
    "": AuxiliaryAttack.CONSTRICTION,

    }










