import math
from operator import mod
import random
import pickle
import json
from collections import defaultdict
from pydantic import BaseModel


class CombatEntity(BaseModel):
    """A ship, turret, or other entity that can attack and take damage."""
    
    kind: str
    name: str
    max_hp: int
    max_shields: int
    hp: int
    shields: int
    firepower: int
    crit_chance: int

    @staticmethod
    def new_ship(kind, name, hp, shields, firepower, crit_chance) -> 'CombatEntity':
        return CombatEntity(
            kind=kind,
            name=name,
            max_hp=hp,
            max_shields=shields,
            hp=hp,
            shields=shields,
            firepower=firepower,
            crit_chance=crit_chance,
        )

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


def new_scout(name: str) -> CombatEntity:
    return CombatEntity.new_ship('scout', name, hp=8, shields=2, firepower=4, crit_chance=0)

def new_destroyer(name: str) -> CombatEntity:
    return CombatEntity.new_ship('destroyer', name, hp=12, shields=6, firepower=6, crit_chance=0)

def new_sniper(name: str) -> CombatEntity:
    return CombatEntity.new_ship('sniper', name, hp=5, shields=0, firepower=10, crit_chance=0)

def new_dreadnought(name: str) -> CombatEntity:
    return CombatEntity.new_ship('dreadnought', name, hp=30, shields=10, firepower=8, crit_chance=0)

def new_planetary_turret(name: str) -> CombatEntity:
    return CombatEntity.new_ship('planetary_turret', name, hp=25, shields=0, firepower=8, crit_chance=0)


# (attacker, defender): 'strong' | 'weak' | 'balanced'
# whether the attacker's attack is strong against the defender
ATTACK_MODIFIERS = defaultdict(lambda: 'balanced', {
    ('scout', 'sniper'): 'strong',
    ('sniper', 'scout'): 'weak',

    ('scout', 'dreadnought'): 'strong',
    ('dreadnought', 'scout'): 'weak',

    ('scout', 'planetary_turret'): 'strong',
    ('planetary_turret', 'scout'): 'weak',

    ('sniper', 'dreadnought'): 'strong',
    ('dreadnought', 'sniper'): 'weak',

    ('dreadnought', 'destroyer'): 'strong',
    ('destroyer', 'dreadnought'): 'weak',
})


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return {
                **o.dict(),
            }
        return super().default(o)

def decode_object_hook(d):
    if 'kind' in d:
        return CombatEntity.parse_obj(d)
    return d


RESET = '\033[0m'


def main():
    entities: list[CombatEntity] = [
        new_sniper('[A] Sniper #1'),
        new_dreadnought('[A] Dreadnought #1'),
        new_scout('[A] Scout #3'),
        new_scout('[A] Scout #4'),
        new_destroyer('[A] Destroyer #2'),
        None,
        new_scout('[D] Scout #1'),
        new_scout('[D] Scout #2'),
        new_destroyer('[D] Destroyer #1'),
        new_planetary_turret('[D] Planetary Turret'),
        # CombatEntity('[D] Deployment Station', hp=20, shields=0, dodge=0, firepower=0),
        # City('[D] Colony', stability=4),
        # City('[D] City', stability=6),
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
                hp_str = f'{entity.shields}/{entity.max_shields} + {entity.hp}/{entity.max_hp}'
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
