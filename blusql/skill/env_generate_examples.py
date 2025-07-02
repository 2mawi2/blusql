import json
from pathlib import Path

from stubs import DbContextProvider, DbContext


def generate_sql_path(db_id) -> Path:
    sql_path = Path(f"test-data/database_schemas/{db_id}.sql")

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file for database ID {db_id} does not exist at {sql_path}")
    
    return sql_path

def fetch_db_context_provider(db_id) -> DbContextProvider:
    sql_path = generate_sql_path(db_id)

    with open(sql_path, 'r') as file:
        sql_schema = file.read()

    db_context_provider = DbContextProvider()
    db_context_provider.get_schema = lambda: DbContext(
        schema=sql_schema,
        db_technology="PostgreSQL Version 10"  # This can be adjusted based on your needs
    )

    return db_context_provider


def generate_examples(path: str='test-data/examples.json'):
    with open(path) as f:
        test_data = json.load(f)

    for example in test_data:
        try:
            db_context_provider = fetch_db_context_provider(example["db_id"])
            example["db_context_provider"] = db_context_provider
            yield example
        except FileNotFoundError as e:
            print(f"Skipping example for {example.get('db_id', 'unknown')}: {e}")
