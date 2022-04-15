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
dt2 = datetime(2022, 11, 1)

parser = argparse.ArgumentParser(description='List module import statements from all commits')

parser.add_argument('-p', '--path',
                    nargs='+', 
                    default=['./libs'],
                    required=True,
                    help='List Python standard library only.')

parser.add_argument('-s', '--std',
                    action="store_true",
                    required=False,
                    help='List Python standard library only.')

parser.add_argument('-n', '--num',
                    type=int,
                    required=False,
                    help='List Python standard library only.')

args = parser.parse_args()


path = args.path

"""
if args.num is not set, it will return None
[:None] is equal [:]
"""
max_num_modules = args.num

# get a list of modules in the standard library.
py_std_libs = sys.stdlib_module_names

#collecting a version of a source file before and after applying a commit
py_libs = {}
for commit in pyd.Repository(path_to_repo=path, clone_repo_to='./libs', since=dt1, to=dt2).traverse_commits():
    for modified_file in commit.modified_files:
        if modified_file.filename.endswith(".py") and modified_file.source_code is not None:
            source_file = iter(modified_file.source_code.split('\n'))
            while line := next(source_file, None):
            #for line in modified_file.source_code.split('\n'):                                
                if 'import ' in line:
                    """
                    simple data 
                    ['from', 'django.contrib.admin.models', 'import', 'ADDITION,', 'CHANGE,', 'DELETION,', 'LogEntry']
                    """
                    data = line.lstrip()
                    # read ahead for mulit-line import
                    if '(' in data:
                        #print(data)
                        while True:
                            next_line = next(source_file, None)
                            data += next_line
                            if ')' in data:
                                break
                    # clean up text
                    data = data.replace('\n', '').replace(',', '').replace('(', '').replace(')', '').split()
                    if 'as' in data:
                        index = data.index('as')
                        data = data[:index]
                    # data[1] will be the name of the module
                    # fillter out local import
                    #if not data[1].startswith('.'):
                    # if --std is set, match with sys.stdlib_module_names
                    if args.std and data[1] not in py_std_libs:
                        continue                   
                    """
                    {'key': [number_of_calls, child{key:number_of_calls}]}
                    """
                    if data[1] in py_libs.keys(): 
                        py_libs[data[1]][0] += 1
                    else:
                        py_libs[data[1]] = [0, dict()]
                        py_libs[data[1]][0] = 1

                    if data[0] == 'from':
                        index = data.index('import') + 1
                        for child in data[index:]:
                            child_dict = py_libs[data[1]][1]
                            child_dict[child] = child_dict.get(child, 0) + 1 
                           

most_used_libs = dict(sorted(py_libs.items(), key=lambda item: item[1][0], reverse=True)[:max_num_modules])
module_tree = Tree("Most called modules")
for k, v in most_used_libs.items():
    current_branch = module_tree.add(k + ' ' + str(v[0]))
    if len(v[1]):
        for child, calls in v[1].items():
            current_branch.add(child + ' '+ str(calls))
print(module_tree)
    
