import sys, time
from type_functions import type_operations
from record_functions import record_operations, BP_TREES
from helpers import clear_bpfile

def operations(input_file, output_file):
    f = open(input_file, "r")
    for line in f:
        line = line[:-1] if line[-1] == "\n" else line
        splitted = [i for i in line.split(" ") if i]
        result = None
        if splitted[1] == "type": 
            result = type_operations(splitted[0], splitted, output_file)
        if splitted[1] == "record": 
            result = record_operations(splitted[0], splitted, output_file)

        with open("horadrimLog.csv", "a") as csv_file:
            result = "success" if result else "failure"
            csv_file.write(str(int(time.time())) + "," + str(line) + "," + str(result) + "\n")

    for type in list(BP_TREES):
        bp_file = "BPTree_" + str(type)
        clear_bpfile(bp_file)
        BP_TREES[type].print_to_file(file = bp_file)

def main(files):
    operations(files[0], files[1])

if __name__ == '__main__':
    main(sys.argv[1:])
