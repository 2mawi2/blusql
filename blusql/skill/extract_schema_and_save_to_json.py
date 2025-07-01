import json
import sqlite3

connection = sqlite3.connect("data/northwind-SQLite3/dist/northwind.db")
cursor = connection.cursor()

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
tables = {}
for table_name, table_sql in cursor.fetchall():
    tables[table_name] = table_sql

with open("schema.json", "w") as f:
    json.dump(tables, f, indent=4)


cursor.execute("SELECT sqlite_version()")
with open("db_technology.txt", "w") as f:
    f.write(f"Database Version: {cursor.fetchone()[0]}")

cursor.close()
connection.close()
