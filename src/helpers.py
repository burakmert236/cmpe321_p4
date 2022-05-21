import constants

def file_read(filename, end_index, start_index=0):
    with open(filename) as fin:
        fin.seek(start_index)
        data = fin.read(end_index - start_index)
        return data

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