import random
from tools import *
from askGPT import *
import argparse
from run import *
from scope_test import *


class EvoPrompt:
    def __init__(self, prompt, method_ids):
        self.prompt = prompt
        self.method_ids = method_ids
    def evaluate(self):
        self.fitness = fitness(self.prompt, method_ids)
        
    def __str__(self):
        return self.prompt

def fitness(prompt, method_ids):
    #TODO: Evaluate with 1 run of ChatUniTest on development set
    # start_generation(method_ids)

    #TODO: extract infomation from scope test for fitness score calculation

    return random.random()

def crossover_and_mutate(p1, p2, method_ids):
    context = {"prompt_1": p1.prompt,  "prompt_2" : p2.prompt}
    messages = generate_messages(TEMPLATE_GA, context)
    llm_response = ask_llm(messages)
    new_prompt = re.search(r'<prompt>(.*?)</prompt>', llm_response, re.DOTALL).group(1).strip()

    o = EvoPrompt(new_prompt, method_ids)
    o.evaluate()
    return o

def roulette_select(population):
    fitnesses = [s.fitness for s in population]
    return random.choices(population, weights=fitnesses)[0]

def ga(method_ids, pop_size=10, generations=5):
    init_prompts = [generate_prompt(f"p{i+1}.jinja2", {}) for i in range(pop_size)]  
    population = []
    for prompt in init_prompts:
        new_sol = EvoPrompt(prompt, method_ids)
        new_sol.evaluate()
        population.append(new_sol)

    for _ in range(generations):
        next_gen = []
        
        while len(next_gen) < len(population):
            # selecting the parents
            p1 = roulette_select(population)
            p2 = roulette_select(population)
            
            # crossover and mutate to generate an offspring
            o = crossover_and_mutate(p1, p2, method_ids)
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

def load_project_data():
    drop_table()
    create_table()
    info_path = Task.parse(project_dir)
    parse_data(info_path)
    clear_dataset()
    export_data()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', action='store_true', help='Enable debugger')
    args = parser.parse_args()
    if args.debug:
        import debugpy
        debugpy.listen(5679)
        print("wait for debugger")
        debugpy.wait_for_client()
        print("attached")

    load_project_data()    
    project_name = os.path.basename(os.path.normpath(project_dir))

    sql_query = f"""
        SELECT id FROM method WHERE project_name='{project_name}' AND class_name='NumberUtils';
    """

    method_ids = [x[0] for x in db.select(script=sql_query)]
    method_ids = method_ids[:3] # Choose 3 methods for testing

    best_sol = ga(method_ids)
    
    save_path = 'best.txt'  # TODO: Change save path
    save_best(save_path, best_sol)