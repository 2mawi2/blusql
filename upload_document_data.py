import hashlib
import json
import os

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(".env", override=True)


TOKEN = os.getenv("PHARIA_AI_TOKEN")
NAMESPACE = os.getenv("PHARIA_DATA_NAMESPACE")
COLLECTION = os.getenv("PHARIA_DATA_COLLECTION")
INDEX = os.getenv("PHARIA_DATA_INDEX")
PHARIA_API_BASE_URL = os.getenv("PHARIA_API_BASE_URL")


def put_document(question: str, query: str, db_id: str):
    # calculate hash on the question
    name = hashlib.sha256(question.encode()).hexdigest()
    url = f"{PHARIA_API_BASE_URL}/studio/search/collections/{NAMESPACE}/{COLLECTION}/docs/{name}"

    payload = json.dumps({
        "schema_version": "V1",
        "contents": [
            {
            "modality": "text",
            "text": question
            }
        ],
        "metadata": [
            {
                "question": question,
                "query": query,
                "db_id": db_id
            }
        ]
        }
    )
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    return response.status_code

def get_documents():
    url = f"{PHARIA_API_BASE_URL}/studio/search/collections/{NAMESPACE}/{COLLECTION}/docs"
    
    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def add_sql_documents_to_db():
    with open('2. Text2SQL/data/DI/examples.json') as f:
        data = json.load(f)


    for item in tqdm(data):
        question = item['question']
        query = item['query']
        db_id = item['db_id']
        
        status_code = None
        retry_count = 0
        max_retries = 5
        
        while status_code != 200 and retry_count < max_retries:
            status_code = put_document(question, query, db_id)
            if status_code == 200:
                # print(f"Document successfully uploaded with status code {status_code}")
                break
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retry {retry_count}/{max_retries} - Status code: {status_code}")
        if status_code != 200:
            print(f"Failed to upload document after {max_retries} attempts. Last status code: {status_code}")


if __name__ == "__main__":
    add_sql_documents_to_db()
    print("All documents uploaded.")
    print("Current documents in the collection:")
    docs = get_documents()
    print(json.dumps(docs, indent=2))