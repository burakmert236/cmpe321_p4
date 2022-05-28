import os
import constants
from BPTree import BPlusTree
from helpers import file_write, file_append

def create_type(type_name, field_number, pk_order, fields):
    # create b+ tree index and write to a file called BPTree_<type_name>
    bp_file = "BPTree_" + type_name
    open(bp_file, 'a').close()
    file_write(bp_file, 0, f"{pk_order}\n")
    fields_line = ",".join([f"{key}:{fields[key]}" for key in fields])
    file_append(bp_file, f"{fields_line}\n")
    file_append(bp_file, "0\n")

def delete_type(type_name):
    # delete b+ tree index file
    # if there is no b+ for the type, write failure into csv
    bplus_file = "BPTree_" + type_name
    bp_files = [f for f in os.listdir('.') if os.path.isfile(f) and bplus_file in f]
    if not bp_files:
        # FAILURE
        pass
    os.remove(bp_files[0])

    record_file_name = type_name + "_records_"
    record_files = [f for f in os.listdir('.') if os.path.isfile(f) and record_file_name in f]
    for f in record_files:
        os.remove(f)

def list_types(output_file):
    files = [(f.split("BPTree_"))[1] for f in os.listdir('.') if os.path.isfile(f) and "BPTree_" in f]
    files.sort()
    with open(output_file, "a") as f:
        for type in files:
            f.write(type + "\n")

def type_operations(operation, args, output_file):
    if operation == "create":
        type_name = args[2]
        field_number = args[3]
        pk_order = args[4]
        fields = { field:args[5:][index*2+1] for index, field in enumerate(args[5::2]) }
        create_type(type_name, field_number, pk_order, fields)
    elif operation == "delete":
        type_name = args[2]
        delete_type(type_name)
    elif operation == "list":
        list_types(output_file)
