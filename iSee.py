"""
iSee, shows the import statment from all the commits
This tools was build, in the progress of learning Python.
It lets me know which libraries are most used and which 
to get familiar with. 
"""
import pydriller as pyd
from datetime import datetime
from rich.tree import Tree
from rich import print
import re
import sys
import argparse

# period to collect data
dt1 = datetime(2019, 11, 1)
dt2 = datetime.now()

parser = argparse.ArgumentParser(description="List module import statements from all commits")

parser.add_argument(
    "-p", "--path", nargs="+", default=["./libs"], required=True, help="List Python standard library only."
)

parser.add_argument("-s", "--std", action="store_true", required=False, help="List Python standard library only.")

parser.add_argument("-n", "--num", type=int, required=False, help="List Python standard library only.")

args = parser.parse_args()

path = args.path

"""
if args.num is not set, it will return None
[:None] is equal [:]
"""
max_num_modules = args.num

# get a list of modules in the standard library.
PY_STD_LIBS = sys.stdlib_module_names


def count_import_statements(py_libs: list) -> list:
    MODULE_NAME = 1
    NUM_IMPORTS = 0
    CHILD_MODULES = 1
    # collecting a version of a source files
    for commit in pyd.Repository(path_to_repo=path, clone_repo_to="./libs", since=dt1, to=dt2).traverse_commits():
        for modified_file in commit.modified_files:
            if modified_file.filename.endswith(".py") and modified_file.source_code is not None:
                source_file = iter(modified_file.source_code.split("\n"))
                while line := next(source_file, None):
                    """
                    only process the import statements
                    """
                    if "import " in line:
                        data = line.lstrip()
                        # read ahead for mulit-line import
                        if "(" in data:
                            # print(data)
                            while True:
                                next_line = next(source_file, None)
                                data += next_line
                                if ")" in data:
                                    break
                        """
                        clean import statement
                        """
                        data = data.replace("\n", "").replace(",", "").replace("(", "").replace(")", "").split()
                        if "as" in data:
                            index = data.index("as")
                            data = data[:index]
                        # if --std is set, match with sys.stdlib_module_names
                        if args.std and data[1] not in PY_STD_LIBS:
                            continue
                        """
                        data formats
                        data = ['from', 'django.contrib.admin.models', 'import', 'ADDITION,', 'CHANGE,', 'DELETION,', 'LogEntry']
                        py_lib = {'key': [number_of_imports, child{key:number_of_imports}]}
                        """
                        if data[MODULE_NAME] in py_libs.keys():
                            py_libs[data[MODULE_NAME]][NUM_IMPORTS] += 1
                        else:
                            py_libs[data[MODULE_NAME]] = [1, dict()]

                        if data[0] == "from":
                            index = data.index("import") + 1
                            for child in data[index:]:
                                child_dict = py_libs[data[MODULE_NAME]][CHILD_MODULES]
                                child_dict[child] = child_dict.get(child, NUM_IMPORTS) + 1

    return py_libs


def show_import_statements(py_libs: list) -> None:
    """
    Show the import statements in descending order
    data format
    {'key': [number_of_imports, child{key:number_of_imports}]}
    """
    DATA_LIST = 1
    NUM_IMPORTS = 0
    MODULE_NAME = 0
    CHILD_MODULES = 1
    """
    Reverse sort by number of imports and limit the number of modules show if --num is set
    """
    most_used_libs = dict(
        sorted(py_libs.items(), key=lambda item: item[DATA_LIST][NUM_IMPORTS], reverse=True)[:max_num_modules]
    )

    module_tree = Tree("Most imported modules")
    for k, v in most_used_libs.items():
        current_branch = module_tree.add(k + " " + str(v[MODULE_NAME]))
        if len(v[CHILD_MODULES]):
            for child, calls in v[CHILD_MODULES].items():
                current_branch.add(child + " " + str(calls))
    print(module_tree)


def main():
    py_libs = {}
    py_libs = count_import_statements(py_libs)
    show_import_statements(py_libs)


if __name__ == "__main__":
    main()
