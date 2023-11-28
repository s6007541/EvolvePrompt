import random
from tools import *
from askGPT import *
import argparse
from run import *
from scope_test import *
from parse_xml import result_analysis

#NOTE: Hyperparameters
POPSIZE = 10
NUM_GENERATION = 5

BASE_PATH = "../prompt/"
SAVE_PATH = os.path.join(BASE_PATH, "evoprompt")
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

class EvoPrompt:
    def __init__(self, prompt, method_ids):
        self.prompt = prompt
        self.method_ids = method_ids
    def evaluate(self):
        self.fitness = fitness(self.prompt, method_ids)
        
    def __str__(self):
        return self.prompt

def fitness(prompt, method_ids):
    result_path = start_generation(method_ids, multiprocess=False, repair=False, evo_prompt=prompt, cand_evolve=True)
    results = result_analysis(result_path)
    score = results['correct-tests'] / results['all-tests']  # Fitness = Correct / Attempts
    return score

def crossover_and_mutate(p1, p2, method_ids):
    print(Fore.GREEN + "*"*20 + "CROSSOVER AND MUTATION" + "*"*20)
    context = {"prompt_1": p1.prompt,  "prompt_2" : p2.prompt}
    messages = generate_messages(TEMPLATE_GA, context)
    llm_response = ask_llm(messages)
    if llm_response:
        try:
            new_prompt = re.search(r'<prompt>(.*?)</prompt>', llm_response, re.DOTALL).group(1).strip()
        except:
            # TODO: handle case when llm_response does not contains <prompt> and </prompt>
            new_prompt = p1.prompt
    else: 
        # TODO: handle case when llm_response return None
        new_prompt = p1.prompt
        
    o = EvoPrompt(new_prompt, method_ids)
    o.evaluate()
    return o

def roulette_select(population):
    fitnesses = [s.fitness for s in population]
    if max(fitnesses) == 0:
        # all fitnesses are 0
        return random.choice(population)
    else:
        return random.choices(population, weights=fitnesses)[0]

def delete_previous_log():
    if os.path.exists(SAVE_PATH):
        file_list = os.listdir(SAVE_PATH)
        for file in file_list:
            file_path = os.path.join(SAVE_PATH, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"File '{file}' deleted.")
            except Exception as e:
                print(f"Error deleting file '{file}': {e}")

def ga(method_ids, pop_size=POPSIZE, generations=NUM_GENERATION):
    delete_previous_log()
    init_prompts = [generate_prompt(f"p{i+1}.jinja2", {}) for i in range(pop_size)]  
    population = []
    for prompt in init_prompts:
        new_sol = EvoPrompt(prompt, method_ids)
        new_sol.evaluate()
        population.append(new_sol)

    for i in range(generations):
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
        print(Fore.YELLOW + f"GENERATION {i + 1}: \n", best_solution, Style.RESET_ALL)
        file_name = f"generation_{i+1}.jinja2"
        save_best(file_name, best_solution)
    return best_solution

def save_best(file_name, solution):
    file_path = os.path.join(SAVE_PATH, file_name)
    with open(file_path, 'w') as f:
        f.write(str(solution))

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
        SELECT id FROM method WHERE project_name='{project_name}';
    """

    method_ids = [x[0] for x in db.select(script=sql_query)]

    if not method_ids:
        raise Exception("Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]

    best_sol = ga(method_ids)
    