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

    def take_damage(self, firepower: int, attacker: 'CombatEntity'):
        modifier = ATTACK_MODIFIERS[(attacker.kind, self.kind)]
        if modifier == 'strong':
            crit_chance = min(attacker.crit_chance + 40, 100)
        else:
            crit_chance = attacker.crit_chance
        print(f'Firepower: {firepower}, effective crit chance: {crit_chance}')

        if random.random() * 100 <= crit_chance:
            print('Critical hit!')
            actual_damage = firepower * 2
        else:
            actual_damage = firepower

        print(f'"{self.name}" takes {actual_damage} damage!')
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
    return CombatEntity.new_ship('scout', name, hp=5, shields=5, firepower=4, crit_chance=30)

def new_destroyer(name: str) -> CombatEntity:
    return CombatEntity.new_ship('destroyer', name, hp=14, shields=8, firepower=7, crit_chance=10)

def new_sniper(name: str) -> CombatEntity:
    return CombatEntity.new_ship('sniper', name, hp=3, shields=7, firepower=10, crit_chance=60)

def new_dreadnought(name: str) -> CombatEntity:
    return CombatEntity.new_ship('dreadnought', name, hp=35, shields=20, firepower=10, crit_chance=35)

def new_planetary_turret(name: str) -> CombatEntity:
    return CombatEntity.new_ship('planetary_turret', name, hp=55, shields=0, firepower=14, crit_chance=20)

def new_mining_ship(name: str) -> CombatEntity:
    return CombatEntity.new_ship('mining_ship', name, hp=2, shields=4, firepower=1, crit_chance=80)

def new_trade_ship(name: str) -> CombatEntity:
    return CombatEntity.new_ship('trade_ship', name, hp=4, shields=0, firepower=0, crit_chance=0)

def new_core_drill(name: str) -> CombatEntity:
    return CombatEntity.new_ship('core_drill', name, hp=15, shields=0, firepower=0, crit_chance=0)

def new_shipyard(name: str) -> CombatEntity:
    return CombatEntity.new_ship('shipyard', name, hp=35, shields=0, firepower=0, crit_chance=0)

def new_mining_depot(name: str) -> CombatEntity:
    return CombatEntity.new_ship('mining_depot', name, hp=25, shields=0, firepower=0, crit_chance=0)

def new_trade_depot(name: str) -> CombatEntity:
    return CombatEntity.new_ship('trade_depot', name, hp=20, shields=0, firepower=0, crit_chance=0)

def new_refinery(name: str) -> CombatEntity:
    return CombatEntity.new_ship('refinery', name, hp=30, shields=0, firepower=0, crit_chance=0)

def new_fabricator(name: str) -> CombatEntity:
    return CombatEntity.new_ship('fabricator', name, hp=30, shields=0, firepower=0, crit_chance=0)

def new_tech_factory(name: str) -> CombatEntity:
    return CombatEntity.new_ship('tech_factory', name, hp=20, shields=0, firepower=0, crit_chance=0)

def new_death_beam(name: str) -> CombatEntity:
    return CombatEntity.new_ship('death_beam', name, hp=10, shields=0, firepower=0, crit_chance=0)

def new_emergency_shields(name: str) -> CombatEntity:
    return CombatEntity.new_ship('emergency_shields', name, hp=25, shields=0, firepower=0, crit_chance=0)

def new_comms_tower(name: str) -> CombatEntity:
    return CombatEntity.new_ship('comms_tower', name, hp=25, shields=0, firepower=0, crit_chance=0)

def new_hacking_terminal(name: str) -> CombatEntity:
    return CombatEntity.new_ship('hacking_terminal', name, hp=20, shields=0, firepower=0, crit_chance=0)


# (attacker, defender): 'strong' | 'weak' | 'balanced'
# whether the attacker's attack is strong against the defender
ATTACK_MODIFIERS = defaultdict(lambda: 'balanced', {
    ('scout', 'sniper'): 'strong',
    ('scout', 'dreadnought'): 'strong',
    ('scout', 'trade_ship'): 'strong',
    ('destroyer', 'scout'): 'strong',
    ('destroyer', 'trade_ship'): 'strong',
    ('destroyer', 'core_drill'): 'strong',
    ('destroyer', 'shipyard'): 'strong',
    ('destroyer', 'mining_depot'): 'strong',
    ('destroyer', 'trade_depot'): 'strong',
    ('destroyer', 'refinery'): 'strong',
    ('destroyer', 'fabricator'): 'strong',
    ('destroyer', 'tech_factory'): 'strong',
    ('destroyer', 'death_beam'): 'strong',
    ('destroyer', 'emergency_shields'): 'strong',
    ('destroyer', 'comms_tower'): 'strong',
    ('destroyer', 'hacking_terminal'): 'strong',
    ('sniper', 'dreadnought'): 'strong',
    ('sniper', 'trade_ship'): 'strong',
    ('sniper', 'planetary_turret'): 'strong',
    ('dreadnought', 'destroyer'): 'strong',
    ('dreadnought', 'trade_ship'): 'strong',
    ('dreadnought', 'planetary_turret'): 'strong',
    ('dreadnought', 'core_drill'): 'strong',
    ('dreadnought', 'shipyard'): 'strong',
    ('dreadnought', 'mining_depot'): 'strong',
    ('dreadnought', 'trade_depot'): 'strong',
    ('dreadnought', 'refinery'): 'strong',
    ('dreadnought', 'fabricator'): 'strong',
    ('dreadnought', 'tech_factory'): 'strong',
    ('dreadnought', 'death_beam'): 'strong',
    ('dreadnought', 'emergency_shields'): 'strong',
    ('dreadnought', 'comms_tower'): 'strong',
    ('dreadnought', 'hacking_terminal'): 'strong',
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
                elif entity.hp < entity.max_hp or entity.shields < entity.max_shields:
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

        atk_entity.attack(def_entity)
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
