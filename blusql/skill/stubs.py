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
            markdown="""# Sales Report Q4 2024

## Executive Summary

This report provides an overview of sales performance for Q4 2024 across all regions.

## Regional Performance

| Region | Revenue ($M) | Growth (%) | Target Met |
|--------|-------------|------------|------------|
| North America | 45.2 | 12.5 | ✓ |
| Europe | 38.7 | 8.3 | ✓ |
| Asia Pacific | 52.1 | 18.9 | ✓ |
| Latin America | 15.4 | -2.1 | ✗ |
| Middle East | 9.8 | 5.6 | ✓ |

## Top Products

| Rank | Product | Units Sold | Revenue ($K) | Avg Price |
|------|---------|------------|--------------|-----------|
| 1 | Pro Suite X | 2,341 | 892.5 | $381.25 |
| 2 | Enterprise Plus | 1,876 | 751.2 | $400.43 |
| 3 | Basic Plan | 5,432 | 543.2 | $100.00 |
| 4 | Premium Access | 3,214 | 482.1 | $150.00 |
| 5 | Starter Kit | 8,765 | 350.6 | $40.00 |

## Monthly Breakdown

| Month | New Customers | Revenue ($M) | Churn Rate (%) |
|-------|---------------|--------------|----------------|
| October | 1,234 | 42.8 | 2.1 |
| November | 1,567 | 48.9 | 1.8 |
| December | 2,103 | 69.5 | 1.5 |

### Key Metrics
- **Total Revenue**: $161.2M
- **YoY Growth**: 11.3%
- **Customer Retention**: 96.2%
- **Average Deal Size**: $127,500""",
            error_message=None
        )
