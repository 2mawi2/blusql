curl -X 'POST' \
    'http://localhost:8080/generate-bluesql' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'authorization: Bearer <TOKEN>' \
    -d '{
      "natural_query": "your query here",
      "schema": null
    }'