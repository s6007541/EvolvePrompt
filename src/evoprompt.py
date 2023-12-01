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
PROJECT_NAME = "Lang" # Gson or Cli
ALPHA = 20

BASE_PROJECT_PATH = "../../projects_dataset/" #NOTE: Gson and Cli already moved out. 
BASE_CANDIDATE_PATH = "../evolve_candidates/"
SAVE_PATH = os.path.join("../prompt/", "evoprompt")
evo_project_dir = os.path.join(BASE_PROJECT_PATH, PROJECT_NAME)

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

class EvoPrompt:
    def __init__(self, prompt, method_ids):
        self.prompt = prompt
        self.method_ids = method_ids
        self.info = {
            "result_path" : None,
            "prompt" : prompt
        }
    
    def evaluate(self):
        result_path = start_generation(self.method_ids, multiprocess=False, repair=False, evo_prompt=self.prompt, evo_project_dir=evo_project_dir)
        results = result_analysis(result_path)
        success_test_rate = results['correct-tests'] / results['all-tests']  # Fitness = Correct / Attempts
        success_method_rate = results["correct-methods"] / NUM_METHODS
        line_rates, branch_rates = results["line-rates"], results["branch-rates"]
        line_rate, branch_rate = get_coverage(line_rates, branch_rates)

        self.fitness = (success_test_rate + success_method_rate) + (line_rate + branch_rate) / 4

        self.info.update({
            "result_path" : result_path,
            "success_method_rate" : success_method_rate,
            "success_test_rate" : success_test_rate,
            "line_rate" : line_rate,
            "branch_rate" : branch_rate,
            "fitness" : self.fitness
        })

    def __str__(self):
        return json.dumps(self.info, indent=2)


def get_coverage(line_rates, branch_rates):
    line_rate, branch_rate = 0, 0
    if len(line_rates):
        line_rate = sum(line_rates) / len(line_rates)
    if len(branch_rates):
        branch_rate = sum(branch_rates) / len(branch_rates)
    return line_rate, branch_rate


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
    #NOTE: only save scope test for best prompt, delete others
    for idv in population:
        dir_path = idv.info["result_path"]
        if dir_path == best_sol_path or dir_path == None:
            continue
        else:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(Fore.RED + f"Remove scope test path: '{dir_path}'", Style.RESET_ALL)

def ga(method_ids, pop_size=POPSIZE, generations=NUM_GENERATION):
    delete_previous_log()
    init_prompts = [generate_prompt(f"p{i+1}.jinja2", {}) for i in range(pop_size)]  
    population = []
    for prompt in init_prompts:
        new_sol = EvoPrompt(prompt, method_ids)
        new_sol.evaluate()
        population.append(new_sol)
    save_population("initial_all.json", population)

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
        print(Fore.YELLOW + f"GENERATION {i + 1}: \n", best_solution, Style.RESET_ALL)
        file_name = f"generation_{i+1}.json"
        save_best(file_name, best_solution)
        file_name_all = f"generation_{i+1}_all.json"
        save_population(file_name_all, population)
        clean_scope_test(extended_population, best_solution.info["result_path"])
    return best_solution

def save_population(file_name, population):
    file_path = os.path.join(SAVE_PATH, file_name)
    population_info = [s.info for s in population]
    with open(file_path, 'w') as f:
        json.dump(population_info, f, indent=2)

def save_best(file_name, best_solution):
    file_path = os.path.join(SAVE_PATH, file_name)
    with open(file_path, 'w') as f:
        json.dump(best_solution.info, f, indent=2)

def load_project_data():
    drop_table()
    create_table()
    info_path = Task.parse(evo_project_dir)
    parse_data(info_path)
    clear_dataset()
    export_data()
    file_candidate = os.path.join(BASE_CANDIDATE_PATH, PROJECT_NAME.lower() + ".txt")
    method_tuples = []
    with open(file_candidate, "r") as f:
        lines = f.readlines()
        for line in lines:
            method_infos = line.split("%")
            method_tuples.append((method_infos[-3], method_infos[-2]))
    
    # delete the old result
    remove_single_test_output_dirs(os.path.abspath(evo_project_dir))
    method_ids = []
    for method_tuple in method_tuples:
        
        sql_query = f"""
            SELECT id FROM method WHERE project_name='{PROJECT_NAME}' AND class_name='{method_tuple[0]}' AND method_name='{method_tuple[1]}';
        """

        method_ids.append(db.select(script=sql_query)[0][0])
    
    if not method_ids:
        raise Exception("Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]
        
    return method_ids

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

    method_ids = load_project_data() 
    
    method_ids = method_ids[:NUM_METHODS] # only pick 16 methods

    best_sol = ga(method_ids)
    