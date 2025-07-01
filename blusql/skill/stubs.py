from typing import List, Dict, Any, Optional
from pydantic import BaseModel

"""
    {
      "question": "What are the names of the three artists who have produced the most songs, and how many works did they produce?",
      "query": "SELECT T1.artist_name ,  count(*) FROM artist AS T1 JOIN song AS T2 ON T1.artist_name  =  T2.artist_name GROUP BY T2.artist_name ORDER BY count(*) DESC LIMIT 3",
      "db_id": "music_1"
    },
"""
class PastQuery(BaseModel):
    question: str
    query: str
    db_id: str

class DbContext(BaseModel):
    db_technology: str
    schema: str

class DbContextProvider:
    
    def get_schema(self) -> DbContext:
#         schema = """
#         CREATE TABLE employee (
#     Employee_ID  INT,
#     PRIMARY KEY (Employee_ID),
#     Name         TEXT,
#     Age          INT,
#     City         TEXT,
#     CONSTRAINT sqlite_autoindex_employee_1 UNIQUE (Employee_ID)
# );
# CREATE TABLE evaluation (
#     Employee_ID   TEXT,
#     Year_awarded  TEXT,
#     Bonus         REAL,
#     CONSTRAINT sqlite_autoindex_evaluation_1 UNIQUE (Employee_ID, Year_awarded),
#     FOREIGN KEY (Employee_ID) REFERENCES employee (Employee_ID),
#     PRIMARY KEY (Employee_ID, Year_awarded)
# );
# CREATE TABLE hiring (
#     Shop_ID       INT,
#     Employee_ID   INT,
#     PRIMARY KEY (Employee_ID),
#     Start_from    TEXT,
#     Is_full_time  bool,
#     CONSTRAINT sqlite_autoindex_hiring_1 UNIQUE (Employee_ID),
#     FOREIGN KEY (Employee_ID) REFERENCES employee (Employee_ID),
#     FOREIGN KEY (Shop_ID) REFERENCES shop (Shop_ID)
# );
# CREATE TABLE shop (
#     Shop_ID          INT,
#     PRIMARY KEY (Shop_ID),
#     Name             TEXT,
#     Location         TEXT,
#     District         TEXT,
#     Number_products  INT,
#     Manager_name     TEXT,
#     CONSTRAINT sqlite_autoindex_shop_1 UNIQUE (Shop_ID)
# );"""
#         db_technology = "PostgreSQL Version 10"
        with open("schema.json", "r") as f:
            schema = f.read()
        with open("db_technology.txt", "r") as f:
            db_technology = f.read()
        return DbContext(
            schema=schema,
            db_technology=db_technology
        )

class VectorSearchResponse(BaseModel):
    similar_queries: List[PastQuery]

class PhariaPastQueryProvider:
    def search_similar_queries(self, natural_query: str) -> VectorSearchResponse:
        return VectorSearchResponse(
            similar_queries=[
                PastQuery(
                    question="What are the names of the three artists who have produced the most songs, and how many works did they produce?",
                    query="SELECT T1.artist_name ,  count(*) FROM artist AS T1 JOIN song AS T2 ON T1.artist_name  =  T2.artist_name GROUP BY T2.artist_name ORDER BY count(*) DESC LIMIT 3",
                    db_id="music_1"
                )
            ]
        )
        
class SqlEngineInput(BaseModel):
    sql_query: str

class SqlEngineOutput(BaseModel):
    markdown: Optional[str]
    error_message: Optional[str]

class SqlEngine:
    def execute(self, input: SqlEngineInput) -> SqlEngineOutput:
        return SqlEngineOutput(
            markdown="markdown data",
            error_message=None
        )
