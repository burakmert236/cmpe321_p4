import os

def create_type(type_name, field_number, pk_order, fields):
    # create b+ tree index and write to a file called BPTree_<type_name>
    print(type_name, field_number, pk_order, fields)

def delete_type(type_name):
    # delete b+ tree index file
    # if there is no b+ for the type, write failure into csv
    # bplus_file = "BPTree_" + type_name
    # bp_files = [f for f in os.listdir('.') if os.path.isfile(f) and bplus_file in f]
    # if not bp_files:
    #     # FAILURE
    #     pass
    # os.remove(bp_files[0])

    record_file_name = type_name + "_records_"
    record_files = [f for f in os.listdir('.') if os.path.isfile(f) and record_file_name in f]
    for f in record_files:
        os.remove(f)

def list_types(output_file):
    files = [(f.split("_records_"))[0] for f in os.listdir('.') if os.path.isfile(f) and "_records_" in f]
    unique_files = set((files))
    with open(output_file, "a") as f:
        for type in unique_files:
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
