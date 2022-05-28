import constants, datetime
from BPTree import BPlusTree, Node, Leaf

def file_read(filename, end_index, start_index=0):
    with open(filename) as fin:
        fin.seek(start_index)
        data = fin.read(end_index - start_index)
        return data

def file_write(filename, start_index, line):
    with open(filename, "r+") as fin:
        fin.seek(start_index)
        fin.write(line)

def file_append(filename, line):
    with open(filename, "a") as fin:
        fin.write(line)

def read_file_header(line):
    is_full, first_available = line.split(" ")
    return {
        "is_full": True if is_full == "0" else False,
        "first_available_page": int(first_available)
    }

def read_page_header(line):
    is_full, first_available = line.split(" ")
    return {
        "is_full": True if is_full == "0" else False,
        "first_available_offset": int(first_available)
    }

def get_record(index):
    file_name, page_number, page_offset = line.split(".")

    # is_full flag(0/1) + space + page_number_length + \n
    file_header_size = constants.FILE_HEADER_LENGTH
    # is_full flag(0/1) + space + offset_length + \n
    page_header_size = constants.PAGE_HEADER_LENGTH
    offset_record_size = (
        ((page_number - 1) * constants.RECORD_PER_PAGE * constants.MAX_RECORD_SIZE) + 
        ((page_offset - 1) * constants.MAX_RECORD_SIZE)
    )

    total_offset = file_header_size + page_header_size + offset_record_size

    return file_read(file_name, total_offset+1+constants.MAX_RECORD_SIZE, total_offset+1)


def create_record_line(fields):
    result = "1"
    for i in range(constants.MAX_NUMBER_OF_FIELDS):
        if i < len(fields):
            result = result + fields[i] + ((constants.FIELD_NAME_MAX_LENGTH - len(fields[i])) * " ")
        else:
            result = result + (constants.FIELD_NAME_MAX_LENGTH * " ")
    result = result + "\n"
    return result


def create_new_record_file(type_name, fields):
    new_type_file_name = f"{type_name}_records_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
    new_type_file = open(new_type_file_name, "w")
    # write initial file header: 0(is_full flag) 1(first empty page)
    new_type_file.write("0 1" + ((constants.FILE_HEADER_LENGTH - 4) * " ") + "\n")
    # write initial page header: 0(is_full flag) 1(first empty line)
    new_type_file.write("0 2" + ((constants.PAGE_HEADER_LENGTH - 4) * " ") + "\n")
    # write record
    new_type_file.write(create_record_line(fields))
    new_type_file.close()
    # get record index
    index = f"{new_type_file_name}.1.1"
    return index

def calculate_offset(page_number, line_number):
    page_headers = page_number * constants.PAGE_HEADER_LENGTH
    record_lines_in_prev_pages = (page_number - 1) * constants.RECORD_PER_PAGE * constants.MAX_RECORD_SIZE
    record_lines_in_current_page = (line_number - 1) * constants.MAX_RECORD_SIZE
    
    return constants.FILE_HEADER_LENGTH + \
            page_headers + record_lines_in_prev_pages + record_lines_in_current_page


def calculate_page_header_offset(page_number):
    page_headers = (page_number - 1) * constants.PAGE_HEADER_LENGTH
    record_lines_in_prev_pages = (page_number - 1) * constants.RECORD_PER_PAGE * constants.MAX_RECORD_SIZE

    return constants.FILE_HEADER_LENGTH + page_headers + record_lines_in_prev_pages


def update_page_header(file, page_header_offset):
    record_line_offset = page_header_offset + constants.PAGE_HEADER_LENGTH
    index = 1
    new_first_empty_line = 1
    while True:
        record_line = file_read(file, record_line_offset + constants.MAX_RECORD_SIZE, record_line_offset)
        if not record_line or record_line[0] == "0":
            new_first_empty_line = index
            break

        index = index + 1
        record_line_offset = record_line_offset + constants.MAX_RECORD_SIZE

    new_first_empty_line_line = str(new_first_empty_line) + ((1 - len(str(new_first_empty_line))) * " ")
    is_page_full = new_first_empty_line > constants.RECORD_PER_PAGE
    new_page_header = f"{int(is_page_full)} {new_first_empty_line_line}"
    file_write(file, page_header_offset, new_page_header)

    return is_page_full

def update_file_header(file, page_header_offset):
    page_header_offset = constants.FILE_HEADER_LENGTH
    new_first_empty_page = 1
    index = 1
    while True:
        page_header_line = file_read(file, page_header_offset + constants.MAX_RECORD_SIZE, page_header_offset)
        if not page_header_line:
            new_first_empty_page = index
            if new_first_empty_page <= constants.PAGE_PER_FILE:
                file_append(file, "0 1" + ((constants.PAGE_HEADER_LENGTH-4) * " ") + "\n")
            break
        if page_header_line[0] == "0":
            new_first_empty_page = index
            break

        index = index + 1
        page_header_offset = page_header_offset + (constants.MAX_RECORD_SIZE * constants.RECORD_PER_PAGE) + constants.PAGE_HEADER_LENGTH

    new_first_empty_page_line = str(new_first_empty_page) + ((1 - len(str(new_first_empty_page))) * " ")
    is_file_full = new_first_empty_page > constants.PAGE_PER_FILE
    new_file_header = f"{int(is_file_full)} {new_first_empty_page_line}"
    file_write(file, 0, new_file_header)

    return is_file_full

def udpate_headers(file, first_empty_line, page_header_offset):

    if first_empty_line == constants.RECORD_PER_PAGE: 
        is_page_full = update_page_header(file, page_header_offset)
        is_file_full = update_file_header(file, page_header_offset)

    else:
        is_page_full = update_page_header(file, page_header_offset)
        if is_page_full:
            update_file_header(file, page_header_offset)


def bptree_from_file(file):

    exists = False
    bp_tree = None
    pk_order = 0
    nodes = {}
    leaf_depth = "0"
    with open(file) as f:
        for index, line in enumerate(f):
            if index < 3: 
                if index == 0:
                    pk_order = int(line[:-1])
                continue
            exists = True

            leading_spaces = len(line) - len(line.lstrip(" "))
            line = line.strip()

            if "_records_" in line:
                leaf_depth = leading_spaces
                keys, values = line.split(" ")
                key_list = keys.split(",")
                value_list = values.split(",")

                node = Leaf()
                node.keys = key_list
                node.values = value_list

            else:
                indexes = line.split(",")
                node = Node()
                node.keys = indexes

            if str(leading_spaces) in list(nodes):
                nodes[str(leading_spaces)].append(node)
            else:
                nodes[str(leading_spaces)] = [node]

            if leading_spaces == 0: 
                bp_tree = BPlusTree(4)
                bp_tree.root = node
        

    if exists:
        for index, key in enumerate(list(nodes)):
            if index == leaf_depth: break
            level_nodes = nodes[key]
            next_level_nodes = list(nodes[str(index+1)])

            for level_node in level_nodes:
                portion = len(level_node.keys) + 1
                for children in next_level_nodes[:portion]:
                    children.parent = level_node
                level_node.values = next_level_nodes[:portion]
                next_level_nodes = next_level_nodes[portion:]

        for index, node in enumerate(nodes[str(leaf_depth)]):
            if index == len(nodes[str(leaf_depth)]) - 1: break
            next_node = nodes[str(leaf_depth)][index+1]
            node.next = next_node
            next_node.prev = node
    else:
        bp_tree = BPlusTree(4)

    return pk_order, bp_tree


def clear_bpfile(file):

    result = ""
    with open(file, "r+") as f:
        for index, line in enumerate(f):
            if index < 3:
                result = result + line
            else: break
        
    open(file, "w").close()
    with open(file, "w") as f:
        f.write(result)