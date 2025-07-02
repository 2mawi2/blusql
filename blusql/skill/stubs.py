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
