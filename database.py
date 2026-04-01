import sqlite3
import os

DB_NAME = "shoe_store.db"
SQL_SCRIPT = "create_db.sql"


def create_database():
    """Создает базу данных и таблицы на основе SQL-скрипта."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    if os.path.exists(SQL_SCRIPT):
        with open(SQL_SCRIPT, "r", encoding="utf-8") as f:
            sql_commands = f.read()
            cursor.executescript(sql_commands)
            print("База данных и таблицы успешно созданы!")
    else:
        print(f"Ошибка: файл {SQL_SCRIPT} не найден.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
