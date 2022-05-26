import os
import constants
from helpers import (
    create_record_line, 
    file_read, 
    file_write, 
    file_append,
    calculate_offset, 
    calculate_page_header_offset, 
    create_new_record_file,
    udpate_headers,
    bptree_from_file
)

BP_TREES = {}
PK_ORDERS = {}

def create_record(type_name, fields):
    # check whether a record file exist
    # read first lines of the record files to find an empty spot
    # if all of them are full or no file exists, create new one
    # write into right spot and update page, file headers
    # find right spot in corresponding b+ tree and save record_index

    bp_file = f"BPTree_{type_name}"
    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name] = bptree_from_file(bp_file)

    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    type_files = []
    for f in files:
        if f[:len(type_name)] == type_name:
            type_files.append(f)

    record_index = ""

    if type_files:
        found = False
        for file in type_files:
            file_header = file_read(file, constants.FILE_HEADER_LENGTH)
            if file_header[0] == "0":
                first_empty_page = int(file_header[2:constants.PAGE_HEADER_LENGTH])
                page_header_offset = calculate_page_header_offset(first_empty_page)
                page_header = file_read(file, page_header_offset+constants.PAGE_HEADER_LENGTH-1, page_header_offset)
                first_empty_line = int(page_header[2:])
                record_offset = calculate_offset(first_empty_page, first_empty_line)
                file_write(file, record_offset, create_record_line(fields))
                record_index = f"{file}.{first_empty_page}.{first_empty_line}"

                udpate_headers(file, first_empty_line, page_header_offset)

                found = True
                break
        if not found:
            record_index = create_new_record_file(type_name, fields)
    else:
        record_index = create_new_record_file(type_name, fields)

    print(fields[PK_ORDERS[type_name]-1], record_index)
    BP_TREES[type_name].__setitem__(fields[PK_ORDERS[type_name]-1], record_index)

def delete_record(type_name, pk):

    bp_file = f"BPTree_{type_name}"
    pk_order = 0
    if type_name not in list(BP_TREES): 
        pk_order, BP_TREES[type_name] = bptree_from_file(bp_file)

    ## get record index from b+ tree
    record_index = BP_TREES[type_name].__getitem__(pk)
    file, page, line = record_index.split(".")

    # update record file
    record_offset = calculate_offset(int(page), int(line))
    record_line = file_read(file, record_offset+constants.MAX_RECORD_SIZE, record_offset)
    if record_line[0] == "1":
        record_line = f"0{record_line[1:]}"
        file_write(file, record_offset, record_line)
    
    # update page header
    page_header_offset = calculate_page_header_offset(int(page))
    page_header = file_read(file, page_header_offset+constants.PAGE_HEADER_LENGTH-1, page_header_offset)
    old_first_empty_line = int(page_header[2:])
    if int(line) < old_first_empty_line:
        new_first_empty_line = str(line) + ((constants.PAGE_HEADER_LENGTH - 3 - len(str(line))) * " ")
        new_page_header = f"0 {new_first_empty_line}"
        file_write(file, page_header_offset, new_page_header)
    
    # update file header
    file_header = file_read(file, constants.FILE_HEADER_LENGTH-1)
    old_first_empty_page = int(file_header[2:])
    if int(page) < old_first_empty_page:
        new_first_empty_page = str(page) + ((constants.FILE_HEADER_LENGTH - 3 - len(str(line))) * " ")
        new_file_header = f"0 {new_first_empty_page}"
        file_write(file, 0, new_file_header)

    # delete from b+ tree
    BP_TREES[type_name].delete(pk)

def update_record(type_name, pk, fields):

    # check given fields
    bp_file = f"BPTree_{type_name}"
    pk_order = 0
    if type_name not in list(BP_TREES): 
        pk_order, BP_TREES[type_name] = bptree_from_file(bp_file)
    
    ## get record index from b+ tree
    record_index = BP_TREES[type_name].__getitem__(pk)
    file, page, line = record_index.split(".")

    updated_line = create_record_line([pk] + fields)
    record_offset = calculate_offset(int(page), int(line))
    record_line = file_write(file, record_offset, updated_line)

def search_record(type_name, pk, output_file):

    bp_file = f"BPTree_{type_name}"
    pk_order = 0
    if type_name not in list(BP_TREES): 
        pk_order, BP_TREES[type_name] = bptree_from_file(bp_file)
    
    ## get record index from b+ tree
    record_index = BP_TREES[type_name].__getitem__(pk)
    file, page, line = record_index.split(".")

    record_offset = calculate_offset(int(page), int(line))
    record_line = file_read(file, record_offset + constants.MAX_RECORD_SIZE, record_offset)
    record_line = " ".join([field for field in (record_line[1:-1]).split(" ") if field != ""])
    
    file_append(output_file, record_line+"\n")


def list_records(type_name, output_file):
    record_file_name = type_name + "_records_"
    record_files = [f for f in os.listdir('.') if os.path.isfile(f) and record_file_name in f]
    for f in record_files:
        with open(f) as file:
            for line in file:
                if(len(line) == constants.MAX_RECORD_SIZE):
                    line = " ".join([field for field in (line[1:-1]).split(" ") if field != ""])
                    file_append(output_file, line+"\n")

def filter_records(type_name, condititon, output_file):
    print(type_name, condititon)


def record_operations(operation, args, output_file):
    if operation == "create":
        type_name = args[2]
        fields = args[3:]
        create_record(type_name, fields)
    elif operation == "delete":
        type_name = args[2]
        pk = args[3]
        delete_record(type_name, pk)
    elif operation == "update":
        type_name = args[2]
        pk = args[3]
        fields = args[4:]
        update_record(type_name, pk, fields)
    elif operation == "search":
        type_name = args[2]
        pk = args[3]
        search_record(type_name, pk, output_file)
    elif operation == "list":
        type_name = args[2]
        list_records(type_name, output_file)
    elif operation == "filter":
        type_name = args[2]
        condition = args[3]
        filter_records(type_name, condition, output_file)