import sys
from type_functions import type_operations
from record_functions import record_operations, BP_TREES
from helpers import clear_bpfile

def read_files(input_file, output_file):
    f = open(input_file, "r")
    for line in f:
        line = line[:-1] if line[-1] == "\n" else line
        splitted = line.split(" ")
        if splitted[1] == "type": type_operations(splitted[0], splitted, output_file)
        if splitted[1] == "record": record_operations(splitted[0], splitted, output_file)

    for type in list(BP_TREES):
        bp_file = f"BPTree_{type}"
        clear_bpfile(bp_file)
        BP_TREES[type].print_to_file(file = bp_file)

def write_files(input_file):
    pass

def main(files):
    read_files(files[0], files[1])

if __name__ == '__main__':
    main(sys.argv[1:])
