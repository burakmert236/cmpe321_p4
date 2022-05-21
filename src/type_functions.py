def create_type(type_name, field_number, pk_order, fields):
    print(type_name, field_number, pk_order, fields)

def delete_type(type_name):
    print(type_name)

def list_types():
    print("list")

def type_operations(operation, args):
    if operation == "create":
        type_name = args[2]
        field_number = args[3]
        pk_order = args[4]
        fields = { field:args[5:][index*2+1] for index, field in enumerate(args[5::2]) }
        create_type(type_name, field_number, pk_order, fields)
    elif operation == "delete":
        delete_type()
    elif operation == "list":
        list_types()
