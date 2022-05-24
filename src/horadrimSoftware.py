import sys
from type_functions import type_operations
from record_functions import record_operations

def read_files(input_file):
    f = open(input_file, "r")
    for line in f:
        line = line[:-1] if line[-1] == "\n" else line
        splitted = line.split(" ")
        if splitted[1] == "type": type_operations(splitted[0], splitted)
        if splitted[1] == "record": record_operations(splitted[0], splitted)

def write_files(input_file):
    pass

def main(files):
    read_files(files[0])
    #write_files(files[1])

if __name__ == '__main__':
    main(sys.argv[1:])
