# pylint: disable=unused-variable
def exists(table, values, conn): # I could do this way better but this works
    selection = table.select()
    for i, _ in enumerate(values):
        selection = selection.where(table.c[list(values.keys())[i]] == list(values.values())[i])

    result = conn.execute(selection)
    rowlen = 0
    for _ in result:
        rowlen += 1
    return rowlen != 0

def insert(table, values, conn):
    try:
        conn.execute(table.insert(), [
            values
        ])
    except:
        raise Exception('Table not found.')

def delete(table, values, conn):
    fetched = fetch(table, values, conn)
    if not fetched:
        raise Exception('Table not found.')

    del_select = table.delete()
    for i, _ in enumerate(values):
        del_select = del_select.where(table.c[list(values.keys())[i]] == list(values.values())[i])
    return conn.execute(del_select)

def fetch(table, values, conn):
    if not exists(table, values, conn):
        return None
    selection = table.select()
    for i, _ in enumerate(values):
        selection = selection.where(table.c[list(values.keys())[i]] == list(values.values())[i])
    return conn.execute(selection)
