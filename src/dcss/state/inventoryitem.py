import re
import string
from enum import Enum

from dcss.state.itemproperty import ItemProperty


class InventoryItem:
    ITEM_VECTOR_LENGTH = 7

    NULL_ITEM_VECTOR = [0, 0, 0, False, ItemProperty.NO_PROPERTY, ItemProperty.NO_PROPERTY, ItemProperty.NO_PROPERTY]

    def __init__(self, id_num, name, quantity, base_type=None):
        self.id_num = int(id_num)
        self.name = name
        self.quantity = quantity
        self.base_type = base_type
        self.item_bonus = 0
        self.cursed = False
        self.properties = []
        self.base_type = base_type

        if base_type is not None:
            self.item_type = ItemType(base_type)

        if self.name:
            if '(curse)' in self.name:
                self.cursed = True
                self.name = self.name.replace("(curse)", "")

            self.simple_name = "{}_{}".format(self.get_letter(),re.sub(r'[+-]?[0-9][0-9]?', '', self.name).strip().replace(" ","_"))

            if '+' in self.name or '-' in self.name:
                m = re.search('[+-][1-9][1-9]?', self.name)
                if m:
                    self.item_bonus = int(m.group(0))
                else:
                    self.item_bonus = 0

        else:
            if self.quantity == 0:
                # Might just be an empty slot that the server is telling us about
                pass
            else:
                print(
                    "\n\nself.name is None, not sure why...args to InventoryItem were id_num={}, name={}, quantity={}, base_type={}\n\n".format(
                        id_num, name, quantity, base_type))
                exit(1)

    def set_base_type(self, base_type):
        self.base_type = base_type

    def get_base_type(self):
        return self.base_type

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_quantity(self):
        return self.quantity

    def set_num_id(self, id_num):
        self.id_num = int(id_num)

    def get_num_id(self):
        return self.id_num

    def get_letter(self):
        return string.ascii_letters[self.id_num]

    def get_item_bonus(self):
        return self.item_bonus

    def is_item_equipped(self):
        return self.equipped

    def unequip(self):
        self.equipped = False

    def equip(self):
        self.equipped = True

    def get_item_type(self):
        """
        Since 0 is a valid value, increase all by 1, so 0 means an empty value
        """
        return 1 + self.base_type

    def get_property_i(self, i):
        if i < len(self.properties):
            return self.properties[i]
        else:
            return ItemProperty.NO_PROPERTY

    def get_item_vector(self):
        """
        * Indicates that item vector value may be repeated, if more than one property.

        Index  Information Contained
        -----  ---------------------
          0    Item Type (Armour, Weapon, etc)
          1    Item Count
          2    Item Bonus ("+x" value)
          3    Item Equipped
          4    Property* (Fire resist, stealth, venom, etc)
          5   Property* (Fire resist, stealth, venom, etc)
          6   Property* (Fire resist, stealth, venom, etc)
        """
        item_vector = []
        item_vector.append(self.get_item_type())
        item_vector.append(self.get_quantity())
        item_vector.append(self.get_item_bonus())
        item_vector.append(self.is_item_equipped())
        item_vector.append(self.get_property_i(0))
        item_vector.append(self.get_property_i(1))
        item_vector.append(self.get_property_i(2))

        assert len(item_vector) == InventoryItem.ITEM_VECTOR_LENGTH
        # Note: If this assert fails, update
        # InventoryItem.ITEM_VECTOR_LENGTH to be the correct value

        return item_vector

    def get_item_pddl(self):
        """
        Returns:
             1. list of pddl object statements where each item has a unique name
             2. list of pddl predicates about that item

        Index  Information Contained
        -----  ---------------------
          0    Item Type (Armour, Weapon, etc)
          1    Item Count
          2    Item Bonus ("+x" value)
          3    Item Equipped
          4    Property* (Fire resist, stealth, venom, etc)
          5   Property* (Fire resist, stealth, venom, etc)
          6   Property* (Fire resist, stealth, venom, etc)
        """

        item_pddl_facts = []

        if self.equipped:
            item_pddl_facts.append("(equipped {})".format(self.simple_name))

        if self.item_bonus != 0:
            item_pddl_facts.append("(item_bonus {} {})".format(self.simple_name, self.item_bonus))

        if self.cursed:
            item_pddl_facts.append("(cursed {})".format(self.simple_name))

        # singleton item types (will never have more than one per item slot in inventory)
        if self.item_type is ItemType.WEAPON:
            item_pddl_facts.append("(weapon {})".format(self.simple_name))
        elif self.item_type is ItemType.ARMOUR:
            item_pddl_facts.append("(armour {})".format(self.simple_name))
        else:
            # items with quantities, so need to provide some quantity information
            if self.quantity == 1:
                item_pddl_facts.append("(only_one_remaining {})".format(self.simple_name))
            elif self.quantity > 1:
                item_pddl_facts.append("(multiple_remaining {})".format(self.simple_name))

            # and don't forget item type for these
            if self.item_type is ItemType.POTION:
                item_pddl_facts.append("(potion {})".format(self.simple_name))
            elif self.item_type is ItemType.SCROLL:
                item_pddl_facts.append("(scroll {})".format(self.simple_name))
            elif self.item_type is ItemType.AMMUNITION:
                item_pddl_facts.append("(ammunition {})".format(self.simple_name))

        return self.simple_name, item_pddl_facts


    @staticmethod
    def get_empty_item_vector():
        item_vector = [0 for i in range(InventoryItem.ITEM_VECTOR_LENGTH)]
        return item_vector

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{}({}) - {} (#={}, base_type={})".format(self.get_letter(), self.id_num, self.get_name(),
                                                         self.get_quantity(), self.get_base_type())


class ItemType(Enum):
    """
    Represents a type of item, enum value matches what the game sends over as 'base_type'
    """

    NULL_ITEM_TYPE = -1

    WEAPON = 0
    AMMUNITION = 1
    ARMOUR = 2
    SCROLL = 5
    POTION = 7


