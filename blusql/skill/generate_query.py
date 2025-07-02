from pharia_skill import ChatParams, Csi, IndexPath, Message, skill
from pydantic import BaseModel
from typing import Optional
from pharia_skill.csi.document_index import SearchResult

from stubs import (
    SqlEngine,
    SqlEngineInput, PastQuery
)

NAMESPACE = "Studio"
COLLECTION = "bluesql-collection"
INDEX = "bluesql-index"

VECTOR_K_SEARCH = 10  # Number of similar queries to retrieve

class DbContext(BaseModel):
    db_technology: str
    schema: str

class Input(BaseModel):
    natural_query: str
    db_context: DbContext = None


class Output(BaseModel):
    sql_query: Optional[str]
    markdown_result: Optional[str]
    explanation: Optional[str]


SQL_GENERATION_PROMPT = """You are an expert SQL query generator for {db_technology}.

Database Schema:
{schema}

Similar Past Queries:
{similar_queries}

User Question: {natural_query}

Generate a SQL query that answers the user's question. Return ONLY the SQL query, no explanations."""

SQL_CORRECTION_PROMPT = """You are an expert SQL query generator for {db_technology}.

Database Schema:
{schema}

User Question: {natural_query}

Previous SQL attempt:
{generated_sql}

Error received:
{error_message}

Please correct the SQL query to fix the error. Return ONLY the corrected SQL query."""

EXPLANATION_PROMPT = """You are an SQL expert. A user asked: "{natural_query}"

We attempted to generate SQL for this query but failed after {max_retries} attempts.

Database Schema:
{schema}

Last attempted SQL:
{generated_sql}

Last error:
{error_message}

Please provide a clear explanation of:
1. Why this query might be failing
2. Whether the user's question makes sense for this database schema
3. Any suggestions for how the user could rephrase their question

Keep the explanation concise and helpful."""


@skill
def generate_query(csi: Csi, input: Input) -> Output:
    db_context = input.db_context
       
    index_path = IndexPath(NAMESPACE, COLLECTION, INDEX)
    search_results: list[SearchResult] = csi.search(index_path, input.natural_query, max_results=VECTOR_K_SEARCH)

    print(f"Search results: {len(search_results)} found for query: {input.natural_query}")

    documents: list[dict] = []
    for search_result in search_results:
        document_metadata = csi.document_metadata(search_result.document_path)
        if isinstance(document_metadata, list) and document_metadata:
            # Assuming the first item in the list is the relevant metadata
            document_metadata = document_metadata[0]
        elif isinstance(document_metadata, dict):
            # If it's a dictionary, we can use it directly
            document_metadata = document_metadata
        else:
            # If it's neither, we skip this result
            continue
        documents.append(document_metadata)

    print(f"Documents retrieved: {len(documents)}")

    similar_queries= [
            PastQuery(
                question=doc.get("question", ""),
                query=doc.get("query", ""),
                db_id=doc.get("db_id", "")
            ) for doc in documents
        ]
    
    print(f"Similar queries extracted: {len(similar_queries)}")

    similar_queries_text = "\n".join([
        f"Question: ```{q.question}```\nSQL: ```{q.query}```\nDatabase: ```{q.db_id}```"
        for q in similar_queries
    ])


    sql_query = generate_sql(csi, input.natural_query, input.db_context, similar_queries_text)

    return Output(
        sql_query=sql_query,
        markdown_result=None,
        explanation="Query generated successfully"
    )

    """
    sql_engine = SqlEngine()
    max_retries = 5
    generated_sql = None
    result = None
    
    for attempt in range(max_retries):
        try:
            if attempt == 0:
                prompt = SQL_GENERATION_PROMPT.format(
                    db_technology=db_context.db_technology,
                    schema=db_context.schema,
                    similar_queries=similar_queries_text,
                    natural_query=input.natural_query
                )
            else:
                prompt = SQL_CORRECTION_PROMPT.format(
                    db_technology=db_context.db_technology,
                    schema=db_context.schema,
                    natural_query=input.natural_query,
                    generated_sql=generated_sql,
                    error_message=result.error_message
                )
        except KeyError as e:
            return Output(
                sql_query=None,
                markdown_result=None,
                explanation=f"Template formatting error: Missing variable {e}"
            )
        
        message = Message.user(prompt)
        params = ChatParams(max_tokens=512)
        response = csi.chat("llama-3.1-8b-instruct", [message], params)
        generated_sql = response.message.content.strip()
        
        result = sql_engine.execute(SqlEngineInput(sql_query=generated_sql))
        
        if result.error_message is None and result.markdown:
            return Output(
                sql_query=generated_sql,
                markdown_result=result.markdown,
                explanation="Sample explaination"
            )
    
    try:
        explanation_prompt = EXPLANATION_PROMPT.format(
            natural_query=input.natural_query,
            max_retries=max_retries,
            schema=db_context.schema,
            generated_sql=generated_sql if generated_sql else "No SQL generated",
            error_message=result.error_message if result else "Unknown error"
        )
    except KeyError as e:
        return Output(
            sql_query=generated_sql,
            markdown_result=None,
            explanation=f"Failed to generate explanation due to template error: {e}"
        )

    explanation_message = Message.user(explanation_prompt)
    explanation_response = csi.chat("llama-3.1-8b-instruct", [explanation_message], ChatParams(max_tokens=512))
    
    return Output(
        sql_query=generated_sql,
        markdown_result=None,
        explanation="Here is the data for the customers you requested, I hope you enjoy watching the tables!"
    )
"""
def generate_sql(csi, natural_query, db_context, similar_queries_text):
    prompt = SQL_GENERATION_PROMPT.format(
        db_technology=db_context.db_technology,
        schema=db_context.schema,
        similar_queries=similar_queries_text,
        natural_query=natural_query
    )
    message = Message.user(prompt)
    params = ChatParams(max_tokens=512)
    response = csi.chat("llama-3.1-8b-instruct", [message], params)
    generated_sql = response.message.content.strip()
    return generated_sql


if __name__ == "__main__":
    from pharia_skill.testing import DevCsi
    dev_csi = DevCsi().with_studio("qa-marius")
    inp = Input(natural_query='find me all customers ')
    generate_query(dev_csi, inp)