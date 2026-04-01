import sqlite3
import pandas as pd
import os

DB_NAME = 'shoe_store.db'
DATA_DIR = 'data'


def get_or_create_id(cursor, table, val, col='name'):
    if pd.isna(val) or str(val).strip() == "": return None
    val = str(val).strip()
    cursor.execute(f"SELECT id FROM {table} WHERE {col} = ?", (val,))
    res = cursor.fetchone()
    if res: return res[0]
    cursor.execute(f"INSERT INTO {table} ({col}) VALUES (?)", (val,))
    return cursor.lastrowid


def run_import():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        path_points = os.path.join(DATA_DIR, 'Пункты выдачи_import.xlsx')
        if os.path.exists(path_points):
            df = pd.read_excel(path_points, header=None)
            for _, row in df.iterrows():
                get_or_create_id(cursor, 'pickup_points', row[0], 'address')
            print("Пункты выдачи загружены")

        path_users = os.path.join(DATA_DIR, 'user_import.xlsx')
        if os.path.exists(path_users):
            df = pd.read_excel(path_users)
            for _, row in df.iterrows():
                role_id = get_or_create_id(cursor, 'roles',
                                           row['Роль сотрудника'])
                cursor.execute(
                    "INSERT OR IGNORE INTO users (login, password, fio, role_id) VALUES (?,?,?,?)",
                    (str(row['Логин']), str(row['Пароль']), str(row['ФИО']),
                     role_id))
            print("Пользователи загружены")

        path_tovar = os.path.join(DATA_DIR, 'Tovar.xlsx')
        if os.path.exists(path_tovar):
            df = pd.read_excel(path_tovar)
            for _, row in df.iterrows():
                cat_id = get_or_create_id(cursor, 'categories',
                                          row['Категория товара'])
                man_id = get_or_create_id(cursor, 'manufacturers',
                                          row['Производитель'])
                sup_id = get_or_create_id(cursor, 'suppliers', row['Поставщик'])
                unit_id = get_or_create_id(cursor, 'units',
                                           row['Единица измерения'])

                cursor.execute('''
                    INSERT OR IGNORE INTO products 
                    (article, name, description, price, discount, quantity, photo_path, 
                     category_id, manufacturer_id, supplier_id, unit_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                               (str(row['Артикул']),
                                str(row['Наименование товара']),
                                str(row['Описание товара']),
                                float(row['Цена']),
                                float(row['Действующая скидка'] or 0),
                                int(row['Кол-во на складе']),
                                str(row['Фото'] or ""), cat_id, man_id, sup_id,
                                unit_id))
            print("Товары загружены")

        conn.commit()
        print("\nИмпорт в БД 'shoe_store.db' успешно завершен!")

    except Exception as e:
        print(f"Ошибка при импорте: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    run_import()