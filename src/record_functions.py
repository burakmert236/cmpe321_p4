def create_record(type_name, fields):
    print(type_name, fields)

def delete_record(type_name, pk):
    print(type_name, pk)

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