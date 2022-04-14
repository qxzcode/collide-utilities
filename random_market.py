import random


RESOURCE_TYPES = [
    'uranium',
    'iron',
    'carbon',
    'silicon',
]


def print_random_offer():
    if random.random() < 0.5:
        # buy resources
        num_resources = random.randint(1, 7)
        resource_type = random.choice(RESOURCE_TYPES)
        credits = random.randint(2 * num_resources, 5 * num_resources)
        print(f'Buy {num_resources} {resource_type} for {credits} credits')
    else:
        # sell resources
        num_resources = random.randint(1, 7)
        resource_type = random.choice(RESOURCE_TYPES)
        credits = random.randint(1 * num_resources, 2 * num_resources)
        print(f'Sell {num_resources} {resource_type} for {credits} credits')


for _ in range(random.randint(2, 6)):
    print_random_offer()
