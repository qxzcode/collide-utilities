import math
from operator import mod
import random
import pickle
import json
from collections import defaultdict
from pydantic import BaseModel


class CombatEntity(BaseModel):
    """A ship, turret, or other entity that can attack and take damage."""
    
    name: str
    max_hp: int
    hp: int
    shields: int
    dodge: int
    firepower: int
    big_shot: bool = False

    def __init__(self, name, hp, shields, dodge, firepower, big_shot=False):
        super().__init__(
            name=name,
            max_hp=hp,
            hp=hp,
            shields=shields,
            dodge=dodge,
            firepower=firepower,
            big_shot=big_shot,
        )

    def __post_init__(self):
        print(f'Created "{self.name}" with dodge chance {self.dodge_chance}')

    @property
    def dodge_chance(self) -> float:
        return 1.0 - math.exp((0 - self.dodge) / 10)

    def take_damage(self, damage, attacker):
        modifier = ATTACK_MODIFIERS[(type(attacker), type(self))]
        if modifier == 'strong':
            dodge_chance = self.dodge_chance / 2
        elif modifier == 'weak':
            dodge_chance = 1.0 - (1.0 - self.dodge_chance)/2
        else:
            dodge_chance = self.dodge_chance
        print(f'Effective dodge chance: {dodge_chance}')

        if attacker.big_shot:
            if random.random() >= dodge_chance:
                actual_damage = damage
            else:
                actual_damage = 0
        else:
            actual_damage = 0
            for _ in range(damage):
                if random.random() >= dodge_chance:
                    actual_damage += 1

        print(f'"{self.name}" takes {actual_damage} (out of {damage} possible) damage!')
        shield_damage = min(actual_damage, self.shields)
        self.shields -= shield_damage

        hp_damage = actual_damage - shield_damage
        self.hp -= hp_damage
        if self.hp <= 0:
            self.hp = 0
            print(f'"{self.name}" was destroyed!')

    def attack(self, other_ship: 'CombatEntity'):
        print(f'"{self.name}" attacks "{other_ship.name}"')
        other_ship.take_damage(self.firepower, self)

    def __repr__(self):
        return f'CombatEntity["{self.name}", hp={self.hp}/{self.max_hp}]'


class City(CombatEntity):
    def __init__(self, name, stability):
        super().__init__(name, hp=stability, shields=0, dodge=0, firepower=0)

    def take_damage(self, damage, attacker):
        print(f'"{self.name}" loses 1 stability point!')
        self.hp -= 1
        if self.hp <= 0:
            self.hp = 0
            print(f'"{self.name}" was conquered!')


class Scout(CombatEntity):
    def __init__(self, name):
        super().__init__(name, hp=8, shields=2, dodge=6, firepower=4)

class Destroyer(CombatEntity):
    def __init__(self, name):
        super().__init__(name, hp=12, shields=6, dodge=4, firepower=6)

class Sniper(CombatEntity):
    def __init__(self, name):
        super().__init__(name, hp=5, shields=0, dodge=6, firepower=10, big_shot=True)

class Dreadnought(CombatEntity):
    def __init__(self, name):
        super().__init__(name, hp=30, shields=10, dodge=0, firepower=8, big_shot=True)

class PlanetaryTurret(CombatEntity):
    def __init__(self, name):
        super().__init__(name, hp=25, shields=0, dodge=0, firepower=8)


# (attacker, defender): 'strong' | 'weak' | 'balanced'
# whether the attacker's attack is strong against the defender
ATTACK_MODIFIERS = defaultdict(lambda: 'balanced', {
    (Scout, Sniper): 'strong',
    (Sniper, Scout): 'weak',

    (Scout, Dreadnought): 'strong',
    (Dreadnought, Scout): 'weak',

    (Scout, PlanetaryTurret): 'strong',
    (PlanetaryTurret, Scout): 'weak',

    (Sniper, Dreadnought): 'strong',
    (Dreadnought, Sniper): 'weak',

    (Dreadnought, Destroyer): 'strong',
    (Destroyer, Dreadnought): 'weak',
})


"""
light_a = CombatEntity("Light A", hp=15, dodge=10, firepower=2)
medium_a = CombatEntity("Medium A", hp=30, dodge=4, firepower=14)
heavy_a = CombatEntity("Heavy A", hp=53, dodge=8, firepower=11)
a_ships = [light_a, medium_a, heavy_a]

light_b = CombatEntity("Light B", hp=13, dodge=8, firepower=8)
medium_b = CombatEntity("Medium B", hp=24, dodge=8, firepower=10)
heavy_b = CombatEntity("Heavy B", hp=50, dodge=8, firepower=13)
b_ships = [light_b, medium_b, heavy_b]
"""


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return {
                '__type__': type(o).__name__,
                **o.dict(),
            }
        return super().default(o)

def decode_object_hook(d):
    if '__type__' in d:
        class_name = d.pop('__type__')
        class_ = globals()[class_name]
        return class_.parse_obj(d)
    return d


RESET = '\033[0m'


def main():
    entities: list[CombatEntity] = [
        Sniper('[A] Sniper #1'),
        Dreadnought('[A] Dreadnought #1'),
        Scout('[A] Scout #3'),
        Scout('[A] Scout #4'),
        Destroyer('[A] Destroyer #2'),
        None,
        Scout('[D] Scout #1'),
        Scout('[D] Scout #2'),
        Destroyer('[D] Destroyer #1'),
        PlanetaryTurret('[D] Planetary Turret'),
        CombatEntity('[D] Deployment Station', hp=20, shields=0, dodge=0, firepower=0),
        City('[D] Colony', stability=4),
        City('[D] City', stability=6),
    ]

    try:
        with open('data.json', 'r') as f:
            entities = json.load(f, object_hook=decode_object_hook)
        print('Loaded saved data.')
    except FileNotFoundError:
        pass

    print()
    while True:
        with open('data.json', 'w') as f:
            json.dump(entities, f, cls=MyJSONEncoder, indent=4)

        for i, entity in enumerate(entities):
            if entity is None:
                print()
            else:
                if entity.hp <= 0:
                    color = '\033[91m'
                elif entity.hp < entity.max_hp:
                    color = '\033[93m'
                else:
                    color = '\033[92m'
                hp_str = f'{entity.shields}+{entity.hp}/{entity.max_hp}'
                print(f'{color}({i})\t{entity.name:24} {hp_str:10}{RESET}')

        print()
        atk_index = get_number('Attacker: ', range(len(entities)))
        atk_entity = entities[atk_index]
        def_index = get_number('Defender: ', range(len(entities)))
        def_entity = entities[def_index]
        do_return_fire = input('Return fire? (y/n) ') == 'y'

        atk_entity.attack(def_entity)
        if do_return_fire and def_entity.hp > 0:
            print('Return fire!')
            def_entity.attack(atk_entity)
        else:
            print('No return fire!')
        print()



def get_number(prompt: str, range_: range):
    while True:
        try:
            number = int(input(prompt))
            if number in range_:
                return number
        except ValueError:
            pass
        print('[invalid] ', end='')


if __name__ == '__main__':
    main()
