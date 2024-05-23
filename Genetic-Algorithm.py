from itertools import compress
import random
import time
import matplotlib.pyplot as plt

from data import *

def initial_population(individual_size, population_size):
    return [[random.choice([True, False]) for _ in range(individual_size)] for _ in range(population_size)]

def fitness(items, knapsack_max_capacity, individual):
    total_weight = sum(compress(items['Weight'], individual))
    if total_weight > knapsack_max_capacity:
        return 0
    return sum(compress(items['Value'], individual))

def population_best(items, knapsack_max_capacity, population):
    best_individual = None
    best_individual_fitness = -1
    for individual in population:
        individual_fitness = fitness(items, knapsack_max_capacity, individual)
        if individual_fitness > best_individual_fitness:
            best_individual = individual
            best_individual_fitness = individual_fitness
    return best_individual, best_individual_fitness


items, knapsack_max_capacity = get_big()
print(items)

population_size = 100
generations = 200
n_selection = 20
n_elite = 2

start_time = time.time()
best_solution = None
best_fitness = 0
population_history = []
best_history = []
population = initial_population(len(items), population_size)

def select_by_roulette(population, fitnesses, n_selection):
    overall_fitness = sum(fitnesses)
    selection_probabilities = list(map(lambda score: score / overall_fitness, fitnesses))
    selected_members = random.choices(population, weights=selection_probabilities, k=n_selection)
    return selected_members
def crossover(parent_a, parent_b):
    division_point = random.randint(1, len(parent_a) - 2)
    offspring_a = parent_a[:division_point] + parent_b[division_point:]
    offspring_b = parent_b[:division_point] + parent_a[division_point:]
    return offspring_a, offspring_b

def mutate(individual):
    mutation_rate = 0.01
    def mutate_gene(gene):
        return not gene if random.random() < mutation_rate else gene

    mutated_entity = list(map(mutate_gene, individual))
    individual[:] = mutated_entity


for _ in range(generations):
    # Zapis historii populacji
    population_history.append(population)
    # licze fitnes dla kazdego osobnika nowej populacji
    fitnesses = [fitness(items, knapsack_max_capacity, individual) for individual in population]
    # wybieram rodzicow do rozmnazania
    potential_parents = select_by_roulette(population, fitnesses, n_selection)
    # tworzenie nowego pokolenia
    next_generation = []
    # Generacja następców z uwzględnieniem elit
    for _ in range((population_size - n_elite) // 2):  # Zakładamy tworzenie dwóch potomków na parę
        parent_one, parent_two = random.sample(potential_parents, 2)
        offspring_one, offspring_two = crossover(parent_one, parent_two)
        mutate(offspring_one)
        mutate(offspring_two)
        next_generation.extend([offspring_one, offspring_two])

    # Znajdowanie elitarnych jednostek w oparciu o ich przystosowanie
    elite_members = sorted(population, key=lambda x: fitness(items, knapsack_max_capacity, x), reverse=True)[:n_elite]
    # Budowanie nowego pokolenia z uwzględnieniem elitarnych jednostek
    next_generation = next_generation[:population_size - len(elite_members)] + elite_members

    population = next_generation

    best_individual, best_individual_fitness = population_best(items, knapsack_max_capacity, population)
    if best_individual_fitness > best_fitness:
        best_solution = best_individual
        best_fitness = best_individual_fitness
    best_history.append(best_fitness)

end_time = time.time()
total_time = end_time - start_time
print('Best solution:', list(compress(items['Name'], best_solution)))
print('Best solution value:', best_fitness)
print('Time: ', total_time)

# plot generations
x = []
y = []
top_best = 10
for i, population in enumerate(population_history):
    plotted_individuals = min(len(population), top_best)
    x.extend([i] * plotted_individuals)
    population_fitnesses = [fitness(items, knapsack_max_capacity, individual) for individual in population]
    population_fitnesses.sort(reverse=True)
    y.extend(population_fitnesses[:plotted_individuals])
plt.scatter(x, y, marker='.')
plt.plot(best_history, 'r')
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.show()
