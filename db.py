# pylint: disable=unused-variable
def exists(table, values, conn): # I could do this way better but this works
    selection = table.select()
    for i in range(len(values)):
        key = list(values.keys())[i]
        val = list(values.values())[i]
        selection = selection.where(table.c[key] == val)
    result = conn.execute(selection)
    rowlen = 0
    for row in result:
        rowlen += 1
    return rowlen != 0

def insert(table, values, conn):
    try:
        conn.execute(table.insert(), [
            values
        ])
    except:
        raise Exception('Table does not exist.')

def delete(table, values, conn):
    fetched = fetch(table, values, conn)
    if not fetched:
        raise Exception('Row not found.')

    del_select = table.delete()
    for i in range(len(values)):
        key = list(values.keys())[i]
        val = list(values.values())[i]
        del_select = del_select.where(table.c[key] == val)
    return conn.execute(del_select)

def fetch(table, values, conn):
    if not exists(table, values, conn):
        return False
    selection = table.select()
    for i in range(len(values)):
        key = list(values.keys())[i]
        val = list(values.values())[i]
        selection = selection.where(table.c[key] == val)
    return conn.execute(selection)
