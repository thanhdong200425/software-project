import sqlite3


def fetch_data_from_table(table, column, condition=None, condition_params=(), fetch_one=False):
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    column_str = ", ".join(column)
    if condition:
        query = f"SELECT {column_str} FROM {table} WHERE {condition}"
        print(query)
        cursor.execute(query, condition_params)
    else:
        query = f"SELECT {column_str} FROM {table}"
        print(query)
        cursor.execute(query)

    data = cursor.fetchone() if fetch_one else cursor.fetchall()
    connection.close()
    return data

def add_new_record(table, column, params=()):
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    column_str = ", ".join(column)
    placeholders = ", ".join(["?"] * len(params))
    query = f"INSERT INTO {table}({column_str}) VALUES ({placeholders})"
    cursor.execute(query, params)
    connection.commit()
    connection.close()