import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('hotel.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_data_from_table(table, column, condition=None, condition_params=(), fetch_one=False):
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    column_str = ", ".join(column)
    if condition:
        query = f"SELECT {column_str} FROM {table} WHERE {condition}"
        cursor.execute(query, condition_params)
    else:
        query = f"SELECT {column_str} FROM {table}"
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


def get_all_rooms():
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    query = "SELECT * FROM room"
    cursor.execute(query)
    rooms = cursor.fetchall()
    connection.commit()
    connection.close()
    return rooms

def read_users():
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    query = "SELECT * FROM user"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users

def validate_user(email, password):
    connection = sqlite3.connect('hotel.db')
    cursor = connection.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    query = "SELECT * FROM user WHERE email = ? AND password = ?"
    cursor.execute(query, (email.strip(), hashed_password))
    user = cursor.fetchone()  
    connection.close()
    return user
  
# authenticated_user = validate_user(email="example@example.com", password="your_password")
# all_users = read_users()

def count_all_records_from_table(table, condition=None, condition_params=()):
    connection = get_db_connection()
    cursor = connection.cursor()
    if condition:
        query = f"SELECT COUNT(*) FROM {table} WHERE {condition}"
        cursor.execute(query, condition_params)
    else:
        query = f"SELECT COUNT(*) FROM {table}"
        cursor.execute(query)

    result = cursor.fetchone()[0]
    return result
