import numpy as np
import matplotlib.pyplot as plt
import random


def avg_damage(firepower, crit_chance) -> float:
    crit_prob = crit_chance / 100
    return firepower * (1 - crit_prob) + (firepower * 2) * crit_prob

def run_simulation(hp, firepower, crit_chance) -> int:
    # note: if the attacker is strong against the defender, +40% chance of a critical hit
    num_hits = 0
    while hp > 0:
        damage = firepower * 2 if random.random() < crit_chance / 100 else firepower
        hp -= damage
        num_hits += 1
    return num_hits

def get_avg_hits(hp, firepower, crit_chance) -> float:
    return np.mean([run_simulation(hp, firepower, crit_chance) for _ in range(10000)])

if True:
    defender_hps = range(1, 100+1)
    plt.plot(defender_hps, [get_avg_hits(hp, 10, 60) for hp in defender_hps])
    plt.xlabel('Defender HP')
    plt.ylabel('Average number of hits to destroy defender')
    plt.show()

crit_chances = range(0, 100+1, 5)
firepowers = range(1, 20+1)

defender_hp = 55
values = np.array([
    [
        # avg_damage(firepower, crit_chance)
        get_avg_hits(defender_hp, firepower, crit_chance)
        for crit_chance in crit_chances
    ]
    for firepower in firepowers
])

target_value = 3.5
goodnesses = np.exp(-np.abs(values - target_value))
plt.matshow(goodnesses, vmin=0, cmap=plt.cm.Blues, alpha=0.5)
# plt.colorbar()
plt.title(f'Defender HP: {defender_hp}')
plt.xlabel('Crit Chance')
plt.xticks(range(len(crit_chances)), crit_chances)
plt.ylabel('Firepower')
plt.yticks(range(len(firepowers)), firepowers)

for x in range(len(crit_chances)):
    for y in range(len(firepowers)):
        text = f'{values[y, x]:.2f}'
        plt.text(x, y, text, va='center', ha='center')

plt.tight_layout()
plt.show()
# quit()


results = np.array([run_simulation(defender_hp, 10, 35+40) for _ in range(10000)])
print(f'mean: {results.mean():.2f}')
plt.hist(results)
plt.xlabel('Number of Hits')
plt.xticks(range(0, max(results)+2, 1))
plt.tight_layout()
plt.show()