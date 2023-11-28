import os.path
import argparse
import time

from tools import *
from database import *
from parse_data import parse_data
from export_data import export_data
from scope_test import start_generation
from parse_xml import result_analysis
from task import Task


def clear_dataset():
    """
    Clear the dataset folder.
    :return: None
    """
    # Delete the dataset folder
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)


def run():
    """
    Generate the test cases with one-click.
    :return: None
    """
    # Delete history data
    drop_table()

    # Create the table
    create_table()

    # Parse project
    info_path = Task.parse(project_dir)

    # Parse data
    parse_data(info_path)

    # clear last dataset
    clear_dataset()

    # Export data for multi-process
    export_data()

    project_name = os.path.basename(os.path.normpath(project_dir))

    # Modify SQL query to test the designated classes.
    sql_query = """
        SELECT id FROM method WHERE project_name='{}';
    """.format(project_name)

    match = re.search(r"project_name\s*=\s*'([\w-]*)'", sql_query)
    if match:
        project_name = match.group(1)
        print(project_name)
    else:
        raise RuntimeError("One project at one time.")
    # delete the old result
    remove_single_test_output_dirs(get_project_abspath())

    method_ids = [x[0] for x in db.select(script=sql_query)]
    if not method_ids:
        raise Exception("Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]

    # assert False
    # Start the whole process
    start_generation(method_ids, sql_query, multiprocess=False, repair=True, confirmed=False)

    # Export the result
    result_analysis()


if __name__ == '__main__':
    # print("Make sure the config.ini is correctly configured.")
    # seconds = 5
    # while seconds > 0:
    #     print(seconds)
    #     time.sleep(1)  # Pause for 1 second
    #     seconds -= 1
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    # use python run.py --debug to enable debugger
    parser.add_argument('--debug', action='store_true', help='Enable debugger')
    args = parser.parse_args()

    if args.debug:
        import debugpy
        debugpy.listen(5679)
        print("wait for debugger")
        debugpy.wait_for_client()
        print("attached")
    run()
