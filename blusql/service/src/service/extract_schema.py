import json
import sqlite3
from pydantic import BaseModel
from typing import Optional

"""
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

"""

class DbContext(BaseModel):
    db_technology: str
    schema: str
    
    def __str__(self):
        return f"DbContext(db_technology='{self.db_technology}', schema='{self.schema[:50]}...')"


def get_db_context() -> DbContext:
    schema = """
        CREATE TABLE employee (
    Employee_ID  INT,
    PRIMARY KEY (Employee_ID),
    Name         TEXT,
    Age          INT,
    City         TEXT,
    CONSTRAINT sqlite_autoindex_employee_1 UNIQUE (Employee_ID)
);
CREATE TABLE evaluation (
    Employee_ID   TEXT,
    Year_awarded  TEXT,
    Bonus         REAL,
    CONSTRAINT sqlite_autoindex_evaluation_1 UNIQUE (Employee_ID, Year_awarded),
    FOREIGN KEY (Employee_ID) REFERENCES employee (Employee_ID),
    PRIMARY KEY (Employee_ID, Year_awarded)
);
CREATE TABLE hiring (
    Shop_ID       INT,
    Employee_ID   INT,
    PRIMARY KEY (Employee_ID),
    Start_from    TEXT,
    Is_full_time  bool,
    CONSTRAINT sqlite_autoindex_hiring_1 UNIQUE (Employee_ID),
    FOREIGN KEY (Employee_ID) REFERENCES employee (Employee_ID),
    FOREIGN KEY (Shop_ID) REFERENCES shop (Shop_ID)
);
CREATE TABLE shop (
    Shop_ID          INT,
    PRIMARY KEY (Shop_ID),
    Name             TEXT,
    Location         TEXT,
    District         TEXT,
    Number_products  INT,
    Manager_name     TEXT,
    CONSTRAINT sqlite_autoindex_shop_1 UNIQUE (Shop_ID)
);
    """
    return DbContext(db_technology="Postgres", schema=schema)