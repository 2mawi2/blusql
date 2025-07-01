from utils.db_service import SQLiteDatabase
from pathlib import Path
import os
import pandas as pd


def query_to_markdown(sql_query: str) -> str:
    # Construct path to the database
    root_dir = Path(__file__).parent
    db_path = os.path.join(
        root_dir, "data", "northwind-SQLite3", "dist", "northwind.db"
    )

    # Connect and query
    db = SQLiteDatabase(db_path)
    try:
        headers, rows = db.query(sql_query)
        df = pd.DataFrame(rows, columns=headers)
        return df.to_markdown(index=False), ""
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        return (
            "",
            f"Query execution failed.\n\n**Error:** `{e}`\n\n```\n{error_details}\n```",
        )
    finally:
        db.disconnect()


if __name__ == "__main__":
    # Example usage (replace with dynamic input later)
    query = "SELECT CustomerID, CompanyName, Country FROM Customers LIMIT 5"
    # query = "SELECT bad_column FROM Customers;"
    markdown, error = query_to_markdown(query)
    if error:
        print(error)
    else:
        print(markdown)
