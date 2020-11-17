import settings
import sqlite3
import random
import math
import os


class Unit(object):
    def __init__(self, tup):

        self.category = tup[0]
        self.name = tup[1]
        self.description = tup[2]
        self.clas = tup[3]
        self.subclass = tup[4]

        self.cost = tup[5]

        self.men = tup[6]
        self.weight = tup[7]
        self.hitpoints = tup[8]
        self.armor = tup[9]
        self.shield = tup[10]
        self.morale = tup[11]
        self.speed = tup[12]
        self.melee_attack = tup[13]
        self.defence = tup[14]
        self.damage = tup[15]
        self.ap = tup[16]
        self.charge = tup[17]
        self.ammunition = tup[18]
        self.range = tup[19]
        self.ranged_attack = tup[20]
        self.ranged_damage = tup[21]
        self.ranged_ap = tup[22]
        self.attributes = tup[23].split(',')

    def attack(self, other, ranged=False, flank=False, charge=False, front=True, advantage=0):
        def get_modifier():
            m = 1 + 0.25 * advantage
            if flank:
                m *= 1.25
            if charge and self.charge > 0:
                m *= (1 + self.charge / 100)

            return m

        attack_skill = self.melee_attack if not ranged else self.ranged_attack
        ratio = min(1, attack_skill / other.defence)
        hits = math.ceil(ratio * self.men * random.uniform(0.75, 1.25))
        hits = min(self.men, max(1, hits))

        ap = max(self.ranged_ap, 0) if ranged else max(self.ap, 0)
        shield = 1 - other.shield if (ranged and front and other.shield >= 0) else 1

        damage = self.damage if not ranged else self.ranged_damage
        total = (((damage * damage) / (2 * other.armor)) * shield + ap) * hits * get_modifier()
        return round(total, 2)

    def resolve(self, other, ranged=False, flank=False, charge=False, front=True, advantage=0):
        damage = self.attack(other, ranged, flank, charge, front, advantage)
        men_before = other.men

        pool = other.men * other.hitpoints
        pool = max(0, pool - damage)
        other.men = math.ceil(pool / other.hitpoints)

        if ranged:
            self.ammunition -= 1

        if other.men != 0:
            morale_bonus = 1.5 if flank else 1
            ratio = (men_before - other.men) / men_before + 0.5
            other.morale -= (men_before - other.men) * other.weight * ratio * morale_bonus
            other.morale = max(math.ceil(other.morale), 0)

        casualties = men_before - other.men

        return damage, casualties

    def as_tuple(self):
        a = [value for name, value in vars(self).items()]
        a[-1] = ','.join(a[-1])
        return tuple(a)

    @staticmethod
    def unit_by_name(unit_name, table='units'):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table} WHERE name='{unit_name}'")
        tup = c.fetchone()
        conn.close()
        if not tup:
            raise FileNotFoundError(f"The unit {unit_name} was not found on DB.")
        return Unit(tup)

    @staticmethod
    def unit_as_tuple(unit_name, table='units'):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table} WHERE name='{unit_name}'")
        tup = c.fetchone()
        conn.close()
        if not tup:
            raise FileNotFoundError(f"The unit {unit_name} was not found on DB.")
        return tup


if __name__ == '__main__':
    pass
