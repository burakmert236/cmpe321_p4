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
TYPE_INFOS = {}

def create_record(type_name, fields):
    # check whether a record file exist
    # read first lines of the record files to find an empty spot
    # if all of them are full or no file exists, create new one
    # write into right spot and update page, file headers
    # find right spot in corresponding b+ tree and save record_index

    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)

    try:
        value = BP_TREES[type_name].__getitem__(fields[PK_ORDERS[type_name]-1])
        if value: return False
    except:
        pass

    for index, field in enumerate(fields):
        if TYPE_INFOS[type_name][index] == "str":
            fields[index] = str(fields[index])
        if TYPE_INFOS[type_name][index] == "int":
            fields[index] = int(fields[index])


    type_files = []
    for f in files:
        if f[:len(type_name)] == type_name:
            type_files.append(f)

    record_index = ""

    if type_files:
        found = False
        for file in type_files:
            file_header = file_read(file, constants.FILE_HEADER_LENGTH + constants.RECORD_PER_FILE_LENGTH, constants.RECORD_PER_FILE_LENGTH)
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

    BP_TREES[type_name].__setitem__(fields[PK_ORDERS[type_name]-1], record_index)
    return True

def delete_record(type_name, pk):

    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)

    ## get record index from b+ tree, if no index failure
    record_index = None
    try:
        record_index = BP_TREES[type_name].__getitem__(pk)
    except:
        return False

    file, page, line = record_index.split(".")

    try:
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
        new_page_header = ""
        if int(line) < old_first_empty_line:
            new_first_empty_line = str(line) + ((constants.PAGE_HEADER_LENGTH - 3 - len(str(line))) * " ")
            new_page_header = f"0 {new_first_empty_line}"
            file_write(file, page_header_offset, new_page_header)
        
        # update file header
        file_header = file_read(file, constants.FILE_HEADER_LENGTH+constants.RECORD_PER_FILE_LENGTH-1, constants.RECORD_PER_FILE_LENGTH)
        old_first_empty_page = int(file_header[2:])
        new_file_header = ""
        if int(page) < old_first_empty_page:
            new_first_empty_page = str(page) + ((constants.FILE_HEADER_LENGTH - 3 - len(str(line))) * " ")
            new_file_header = f"0 {new_first_empty_page}"
            file_write(file, constants.RECORD_PER_FILE_LENGTH, new_file_header)

        empty_page_header = "0 1" + ((constants.PAGE_HEADER_LENGTH - 4) * " ") + "\n"
        empty_file_header = "0 1" + ((constants.FILE_HEADER_LENGTH - 4) * " ") + "\n"
        if new_page_header == empty_page_header and new_file_header == empty_file_header:
            os.remove(file)

        # update record count line
        record_count_line = file_read(file, constants.RECORD_PER_FILE_LENGTH)
        new_record_count = int(str(record_count_line)) - 1
        new_record_count_line = str(new_record_count) + ((constants.RECORD_PER_FILE_LENGTH - 1 - len(str(new_record_count))) * " ")
        file_write(file, 0, new_record_count_line)
        if new_record_count == 0:
            os.remove(file)
    
    except:
        return False

    # delete from b+ tree
    BP_TREES[type_name].delete(pk)
    return True

def update_record(type_name, pk, fields):

    # check given fields
    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)
    
    record_index = None
    try:
        ## get record index from b+ tree
        record_index = BP_TREES[type_name].__getitem__(pk)
    except:
        return False

    file, page, line = record_index.split(".")

    updated_line = create_record_line(fields)
    record_offset = calculate_offset(int(page), int(line))
    record_line = file_write(file, record_offset, updated_line)

    return True

def search_record(type_name, pk, output_file=None):

    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)
    
    ## get record index from b+ tree
    record_index = None
    try:
        ## get record index from b+ tree
        record_index = BP_TREES[type_name].__getitem__(pk)
    except:
        return False

    file, page, line = record_index.split(".")

    record_offset = calculate_offset(int(page), int(line))
    record_line = file_read(file, record_offset + constants.MAX_RECORD_SIZE, record_offset)
    record_line = " ".join([field for field in (record_line[1:-1]).split(" ") if field != ""])

    if not record_line: return False

    if output_file: file_append(output_file, record_line+"\n")

    return record_line + "\n"


def list_records(type_name, output_file):

    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)

    try:
        first_leaf = BP_TREES[type_name].root
        while True:
            if not first_leaf.values: break
            if isinstance(first_leaf.values[0], str): break
            first_leaf = first_leaf.values[0]

        indexes = []
        leaf = first_leaf
        while True:
            if leaf.values: indexes.extend(leaf.values)
            if not leaf.next: break
            leaf = leaf.next

        if not indexes: return False

        for index in indexes:
            file, page, line = index.split(".")

            record_offset = calculate_offset(int(page), int(line))
            record_line = file_read(file, record_offset + constants.MAX_RECORD_SIZE, record_offset)
            record_line = " ".join([field for field in (record_line[1:-1]).split(" ") if field != ""])
            
            if output_file: file_append(output_file, record_line+"\n")
    except:
        return False

    return True


def filter_records(type_name, condititon, output_file):

    bp_file = f"BPTree_{type_name}"
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if bp_file not in files: return False

    if type_name not in list(BP_TREES): 
        PK_ORDERS[type_name], BP_TREES[type_name], TYPE_INFOS[type_name] = bptree_from_file(bp_file)

    try:
        if "=" in condititon:
            field, value = condititon.split("=")
            field = field.strip()
            value = value.strip()

            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "int":
                value = int(value)
            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "str":
                value = str(value)

            record_line = search_record(type_name, value)
            if not record_line: return False
            file_append(output_file, record_line)

        if "<" in condititon:
            field, value = condititon.split("<")
            field = field.strip()
            value = value.strip()

            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "int":
                value = int(value)
            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "str":
                value = str(value)

            inserted_node = BP_TREES[type_name].find(value)
            
            indexes = []

            for index, leaf_value in enumerate(inserted_node.keys):
                if leaf_value < value: 
                    indexes.append(inserted_node.values[index])

            indexes = indexes[::-1]
        
            while True:
                if not inserted_node.prev: break
                inserted_node = inserted_node.prev
                indexes.extend(inserted_node.values[::-1])

            indexes = indexes[::-1]

            if not indexes: return False

            for index in indexes:

                file, page, line = index.split(".")

                record_offset = calculate_offset(int(page), int(line))
                record_line = file_read(file, record_offset + constants.MAX_RECORD_SIZE, record_offset)
                record_line = " ".join([field for field in (record_line[1:-1]).split(" ") if field != ""])
                file_append(output_file, record_line + "\n")

        if ">" in condititon:
            
            field, value = condititon.split(">")
            field = field.strip()
            value = value.strip()

            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "int":
                value = int(value)
            if TYPE_INFOS[type_name][PK_ORDERS[type_name]-1] == "str":
                value = str(value)

            inserted_node = BP_TREES[type_name].find(value)
            
            indexes = []
            for index, leaf_value in enumerate(inserted_node.keys):
                if leaf_value > value: 
                    indexes.append(inserted_node.values[index])

        
            while True:
                if not inserted_node.next: break
                inserted_node = inserted_node.next
                indexes.extend(inserted_node.values)

            if not indexes: return False

            for index in indexes:

                file, page, line = index.split(".")

                record_offset = calculate_offset(int(page), int(line))
                record_line = file_read(file, record_offset + constants.MAX_RECORD_SIZE, record_offset)
                record_line = " ".join([field for field in (record_line[1:-1]).split(" ") if field != ""])
                file_append(output_file, record_line + "\n")

    except:
        return False

    return True


def record_operations(operation, args, output_file):
    if operation == "create":
        type_name = args[2]
        fields = args[3:]
        return create_record(type_name, fields)
    elif operation == "delete":
        type_name = args[2]
        pk = args[3]
        return delete_record(type_name, pk)
    elif operation == "update":
        type_name = args[2]
        pk = args[3]
        fields = args[4:]
        return update_record(type_name, pk, fields)
    elif operation == "search":
        type_name = args[2]
        pk = args[3]
        return search_record(type_name, pk, output_file)
    elif operation == "list":
        type_name = args[2]
        return list_records(type_name, output_file)
    elif operation == "filter":
        type_name = args[2]
        condition = args[3]
        return filter_records(type_name, condition, output_file)