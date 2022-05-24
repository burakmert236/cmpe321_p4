import constants, datetime

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
    file_header_size = 1 + 1 + len(str(constants.PAGE_PER_FILE)) + 1
    # is_full flag(0/1) + space + offset_length + \n
    page_header_size = page_number * (1 + 1 + len(str(constants.RECORD_PER_PAGE)) + 1)
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
    new_type_file = open(f"{type_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}", "w")
    # write initial file header: 0(is_full flag) 1(first empty page)
    new_type_file.write("0 1  \n")
    # write initial page header: 0(is_full flag) 1(first empty line)
    new_type_file.write("0 2 \n")
    # write record
    new_type_file.write(create_record_line(fields))
    new_type_file.close()
    # get record index
    index = f"{type_name}.1.1"
    return index

def calculate_offset(page_number, line_number):
    file_header = 6
    page_headers = page_number * 5
    record_lines_in_prev_pages = (page_number - 1) * constants.RECORD_PER_PAGE * constants.MAX_RECORD_SIZE
    record_lines_in_current_page = (line_number - 1) * constants.MAX_RECORD_SIZE
    
    return file_header + page_headers + record_lines_in_prev_pages + record_lines_in_current_page


def calculate_page_header_offset(page_number):
    file_header = 6
    page_headers = (page_number - 1) * 5
    record_lines_in_prev_pages = (page_number - 1) * constants.RECORD_PER_PAGE * constants.MAX_RECORD_SIZE

    return file_header + page_headers + record_lines_in_prev_pages


def update_page_header(file, page_header_offset):
    record_line_offset = page_header_offset + 5
    index = 1
    new_first_empty_line = 1
    while True:
        record_line = file_read(file, record_line_offset + constants.MAX_RECORD_SIZE, record_line_offset)
        print(record_line)
        if not record_line or record_line[0] == "0":
            new_first_empty_line = index
            break

        index = index + 1
        record_line_offset = record_line_offset + constants.MAX_RECORD_SIZE

    new_first_empty_line_line = str(new_first_empty_line) + ((2 - len(str(new_first_empty_line))) * " ")
    is_page_full = new_first_empty_line > constants.RECORD_PER_PAGE
    new_page_header = f"{int(is_page_full)} {new_first_empty_line_line}"
    file_write(file, page_header_offset, new_page_header)

    return is_page_full

def update_file_header(file, page_header_offset):
    page_header_offset = 6
    new_first_empty_page = 1
    index = 1
    while True:
        page_header_line = file_read(file, page_header_offset + constants.MAX_RECORD_SIZE, page_header_offset)
        print(page_header_line)
        if not page_header_line:
            new_first_empty_page = index
            if new_first_empty_page <= constants.PAGE_PER_FILE:
                file_append(file, "0 1 \n")
            break
        if page_header_line[0] == "0":
            new_first_empty_page = index
            break

        index = index + 1
        page_header_offset = page_header_offset + (constants.MAX_RECORD_SIZE * constants.RECORD_PER_PAGE) + 6

    new_first_empty_page_line = str(new_first_empty_page) + ((3 - len(str(new_first_empty_page))) * " ")
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
            udpate_file_header()

