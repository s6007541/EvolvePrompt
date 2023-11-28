"""
This file is for starting a scope test for selected methods.
It will automatically create a new folder inside dataset as well as result folder.
The folder format is "scope_test_YYYYMMDDHHMMSS_Direction".
The dataset folder will contain all the information in the direction.
"""
from tools import *
from askGPT import start_whole_process
from database import db
from task import Task
from colorama import Fore, Style, init

init()


def create_dataset_result_folder(direction):
    """
    Create a new folder for this scope test.
    :param direction: The direction of this scope test.
    :return: The path of the new folder.
    """
    # Get current time
    now = datetime.datetime.now()
    # format the time as a string
    time_str = now.strftime("%Y%m%d%H%M%S")
    result_path = os.path.join(result_dir, "scope_test%" + time_str + "%" + direction)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    else:
        raise Exception("Result folder already exists.")
    return result_path


def create_new_folder(folder_path: str):
    """
    Create a new folder.
    :param folder_path: The folder path.
    :return: None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        raise Exception("Folder already exists.")


def find_all_files(folder_path: str, method_ids: list = None):
    """
    Find all the files in the folder.
    :param method_ids: The method ids need to be found.
    :param folder_path: The folder path.
    :return: The file list.
    """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.split("%")[0] not in method_ids:
                continue
            file_list.append(file)
    return file_list


def start_generation(method_ids, sql_query=None, multiprocess=False, repair=True, confirmed=False, evo_prompt=None):
    """
    Start the scope test.
    :param multiprocess: if it needs to
    :param repair:
    :param sql_query:
    :return:
    """
    
    print("You are about to start the whole process of scope test.")
    print("The number of methods is ", len(method_ids), ".")
    record = "This is a record of a scope test.\n"
            
    # Create the new folder
    result_path = create_dataset_result_folder("")

    record += "Result path: " + result_path + "\n"
    if sql_query:
        record += 'SQL script: "' + sql_query + '"\n'
    record += "Included methods: " + str(method_ids) + "\n"

    record_path = os.path.join(result_path, "record.txt")
    with open(record_path, "w") as f:
        f.write(record)
    print(Fore.GREEN + "The record has been saved at", record_path, Style.RESET_ALL)

    # Find all the files
    source_dir = os.path.join(dataset_dir, "direction_1")

    start_whole_process(method_ids, source_dir, result_path, multiprocess=multiprocess, repair=repair, evo_prompt=evo_prompt)
    print("WHOLE PROCESS FINISHED")
    # Run accumulated tests
    project_path = os.path.abspath(project_dir)
    print("START ALL TESTS")

    Task.all_test(result_path, project_path)
    try:
        with open(record_path, "a") as f:
            f.write("Whole test result at: " + find_result_in_projects() + "\n")
    except Exception as e:
        print("Cannot save whole test result.")
        print(e)

    print("SCOPE TEST FINISHED")


if __name__ == '__main__':
    sql_query = "SELECT id FROM method WHERE project_name='Lang_1_f' AND class_name='NumberUtils' AND is_constructor=0;"
    start_generation(sql_query, multiprocess=True, repair=True, confirmed=False)
