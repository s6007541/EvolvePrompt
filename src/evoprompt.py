import random


class Solution:
    def __init__(self, sol):
        self.sol = sol
        
    def evaluate(self):
        self.fitness = fitness(self.sol)
        
    def __str__(self):
        return self.sol

def get_init_prompts(orig_prompt, num_prompts):
    orig_sol = Solution(orig_prompt)
    orig_sol.evaluate()
    init_prompts = [orig_sol]
    for _ in range(num_prompts - 1):
        # TODO: Ask LLM to rephrase the original prompt
        new_sol = Solution(orig_prompt)
        ###############################################
        new_sol.evaluate()
        init_prompts.append(new_sol)
    return init_prompts

def fitness(solution):
    # TODO: Evaluate with 1 run of ChatUniTest on development set
    return random.random()
    ###############################################

def crossover_and_mutate(p1, p2):
    instruction_template = """Please follow the instruction step-by-step to generate a better prompt.
1. Cross over the following prompts and generate a new prompt:
Prompt 1: {}
Prompt 2: {}
2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and </prompt>."""
    instruction = instruction_template.format(p1, p2)
    # TODO: Instruct LLM to do crossover and mutation
    o = Solution(str(p1))
    ###############################################
    
    o.evaluate()
    return o

def roulette_select(population):
    fitnesses = [s.fitness for s in population]
    return random.choices(population, weights=fitnesses)[0]

def ga(pop_size=10, generations=5):
    orig_prompt = 'This is a dummy prompt.'  # TODO: Original prompt from ChatUniTest
    population = get_init_prompts(orig_prompt, pop_size)
    
    for i in range(generations):
        next_gen = []
        
        while len(next_gen) < len(population):
            # selecting the parents
            p1 = roulette_select(population)
            p2 = roulette_select(population)
            
            # crossover and mutate to generate an offspring
            o = crossover_and_mutate(p1, p2)
            
            next_gen.append(o)
            
        # now we have the full next gen
        population.extend(next_gen)
        population = sorted(population, key=lambda x: x.fitness, reverse=True)
        population = population[:pop_size]
        
        best_solution = population[0]
        # print(i + 1, best_solution, best_solution.fitness)
        
    return best_solution

def save_best(filename, solution):
    # TODO: Change to Jinja2 format?
    with open(filename, 'w') as f:
        f.write(str(solution))
    #################################


if __name__ == '__main__':
    best_sol = ga()
    save_path = 'best.txt'  # TODO: Change save path
    save_best(save_path, best_sol)