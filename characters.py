"""
Module containing classes that represent characters
"""
import random
from typing import *


class Character:
    def __init__(self, name: str, hp: int, dex: int, stren: int, prof: int, weapon_die: int, finesse: bool):
        """
        Creates a new character with the given stats

        :param name: a string, this character's name (and UID)
        :param hp: an int, the maximum HP
        :param dex: an int, the Dexterity score
        :param stren: an int, the Strength score
        :param prof: an int, the character's proficiency bonus
        :param weapon_die: an int, the size of the die that is rolled to determine a weapon's damage
        :param finesse: a boolean, True if the weapon is finesse
        """
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.dex = dex
        self.stren = stren
        self.prof = prof
        self.weapon_die = weapon_die
        self.finesse = finesse

    @property
    def dex_mod(self) -> int:
        """
        :return: an int, this character's dexterity modifier
        """
        return (self.dex - 10) // 2

    @property
    def str_mod(self) -> int:
        """
        :return: an int, this character's strength modifier
        """
        return (self.stren - 10) // 2

    @property
    def weapon_bonus(self) -> int:
        """
        :return: an int, the character's best bonus
        """
        return max(self.dex_mod, self.str_mod) if self.finesse else self.str_mod

    @property
    def ac(self) -> int:
        """
        :return: an int, this character's armor class
        """
        return 10 + self.dex_mod

    def roll_initiative(self) -> Tuple[int, int]:
        """
        :return: a tuple of ints, this character's initiative followed by their dex score (for tiebreaks)
        """
        return random.randint(1, 20) + self.dex_mod, self.dex

    def roll_to_hit(self) -> int:
        """
        :return: an int, the value this character has rolled to hit
        """
        return random.randint(1, 20) + self.weapon_bonus + self.prof

    def roll_damage(self) -> int:
        """
        :return: an int, the amount of damage this character does
        """
        return random.randint(1, self.weapon_die) + self.weapon_bonus

    def __hash__(self):
        return hash(self.name)
