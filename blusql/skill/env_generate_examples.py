import json
from pathlib import Path


def generate_sql_path(db_id) -> Path:
    sql_path = Path(f"test-data/database_schemas/{db_id}.sql")

    if not sql_path.exists():
        raise FileNotFoundError(
            f"SQL file for database ID {db_id} does not exist at {sql_path}"
        )

    return sql_path


def fetch_db_schema(db_id) -> str:
    sql_path = generate_sql_path(db_id)

    with open(sql_path, "r") as file:
        sql_schema = file.read()

    return sql_schema


def generate_examples(path: str = "test-data/examples.json"):
    with open(path) as f:
        test_data = json.load(f)

    for example in test_data:
        try:
            db_schema = fetch_db_schema(example["db_id"])
            example["db_schema"] = db_schema
            yield example
        except FileNotFoundError as e:
            print(f"Skipping example for {example.get('db_id', 'unknown')}: {e}")
