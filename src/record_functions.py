import os
import constants
from helpers import (
    create_record_line, 
    file_read, 
    file_write, 
    calculate_offset, 
    calculate_page_header_offset, 
    create_new_record_file,
    udpate_headers,
)

def create_record(type_name, fields):
    # check whether a record file exist
    # read first lines of the record files to find an empty spot
    # if all of them are full or no file exists, create new one
    # write into right spot and update page, file headers
    # find right spot in corresponding b+ tree and save record_index

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


    ## save record index into b+ tree

def delete_record(type_name, pk):

    ## get record index from b+ tree
    record_index = "angel_20220524141303610.1.4"
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

def update_record(type_name, pk, fields):
    print(type_name, pk, fields)

def search_record(type_name, pk):
    print(type_name, pk)

def list_records(type_name):
    print(type_name)

def filter_records(type_name, condititon):
    print(type_name, condititon)


def record_operations(operation, args):
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
        search_record(type_name, pk)
    elif operation == "list":
        type_name = args[2]
        list_records(type_name)
    elif operation == "filter":
        type_name = args[2]
        condition = args[3]
        filter_records(type_name, condition)