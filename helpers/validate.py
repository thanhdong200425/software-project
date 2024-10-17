from database.database_function import fetch_data_from_table


def is_existing_data(table, condition, condition_value):
    result = fetch_data_from_table(table, ['*'], f'{condition} = ?', (condition_value, ), fetch_one=True)
    return result if result and len(result) > 0 else False
