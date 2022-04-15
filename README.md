## What is iSee

iSee, shows the import statment from all the commits
This tools was build, in the progress of learning Python.
It lets me know which libraries are most used and which 
to get familiar with. 

## Usage

Show help message
```
python iSee.py --help 
```

Show analyse remote and local repo
```
python iSee.py -p https://github.com/pandas-dev/pandas.git ./libs/numpy
``` 
* The repo will be cloned to `./libs`

Show standard library only
```
python iSee.py -p https://github.com/pandas-dev/pandas.git ./libs/numpy -s
``` 

