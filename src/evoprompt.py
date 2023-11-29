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
NUM_METHODS = 16
PROJECT_NAME = "Gson" # Gson or Cli

BASE_PROJECT_PATH = "../../" #NOTE: Gson and Cli already moved out. 
BASE_CANDIDATE_PATH = "../evolve_candidates/"
SAVE_PATH = os.path.join("../prompt/", "evoprompt")

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

class EvoPrompt:
    def __init__(self, prompt, method_ids):
        self.prompt = prompt
        self.method_ids = method_ids
        self.result_path = None

    def evaluate(self):
        self.fitness = fitness(self, method_ids)
    
    def __str__(self):
        return self.prompt

def fitness(sol, method_ids):
    result_path = start_generation(method_ids, multiprocess=False, repair=False, evo_prompt=sol.prompt)
    sol.result_path = result_path
    results = result_analysis(result_path)
    score = results['correct-tests'] / results['all-tests']  # Fitness = Correct / Attempts
    return score

def crossover_and_mutate(p1, p2, method_ids):
    print(Fore.GREEN + "*"*20 + "CROSSOVER AND MUTATION" + "*"*20)
    context = {"prompt_1": p1.prompt,  "prompt_2" : p2.prompt}
    messages = generate_messages(TEMPLATE_GA, context)
    # llm_response = ask_llm(messages)
    llm_response = ask_chatgpt(messages)
    if llm_response:
        try:
            new_prompt = re.search(r'<prompt>(.*?)</prompt>', llm_response, re.DOTALL).group(1).strip()
        except:
            print(Fore.RED + "LLM response does not contains <prompt> and </prompt>", Style.RESET_ALL)
            return p1
    else: 
        print(Fore.RED, "LLM response return None", Style.RESET_ALL)
        return p1
        
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
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(Fore.RED + f"File '{file}' deleted.", Style.RESET_ALL)

def clean_scope_test(population, best_sol_path):
    #TODO: only save scope test for best prompt, delete others
    for idv in population:
        if idv.result_path == best_sol_path or idv.result_path == None:
            continue
        else:
            dir_path = idv.result_path
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(Fore.RED + f"Remove scope test path: '{idv.result_path}'", Style.RESET_ALL)

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
        extended_population = copy.deepcopy(population)
        population = population[:pop_size]
        
        best_solution = population[0]
        best_fitness = best_solution.fitness
        print(Fore.YELLOW + f"GENERATION {i + 1}: fitness = {best_fitness} \n", best_solution, Style.RESET_ALL)
        file_name = f"generation_{i+1}.json"
        save_best(file_name, best_solution.prompt, best_fitness)
        clean_scope_test(extended_population, best_solution.result_path)
    return best_solution

def save_best(file_name, prompt, fitness_score):
    file_path = os.path.join(SAVE_PATH, file_name)
    dct = {
        "prompt": prompt,
        "project_name" : PROJECT_NAME,
        "fitness" : fitness_score
    }
    with open(file_path, 'w') as f:
        json.dump(dct, f, indent=2)

def load_project_data():
    current_prj_dir = os.path.join(BASE_PROJECT_PATH, PROJECT_NAME)
    drop_table()
    create_table()
    info_path = Task.parse(current_prj_dir)
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

    method_ids = []
    file_candidate = os.path.join(BASE_CANDIDATE_PATH, PROJECT_NAME.lower() + ".txt")
    with open(file_candidate, "r") as f:
        lines = f.readlines()
        for line in lines:
            id = line.split("%")[0]
            method_ids.append(id)
    
    method_ids = method_ids[:NUM_METHODS] # only pick 16 methods

    best_sol = ga(method_ids)
    