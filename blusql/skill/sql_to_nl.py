from pharia_skill import ChatParams, Csi, Message, skill
from pydantic import BaseModel


class Input(BaseModel):
    sql_table_markdown: str


class Output(BaseModel):
    natural_language_expressions: list[str]


@skill
def sql_to_natural_language(csi: Csi, input: Input) -> Output:
    content = f"""You are an expert in SQL and natural language processing. Your task is to analyze the given SQL table structure in markdown format and extract meaningful natural language expressions that describe what this table represents and what kind of data it contains.

Please provide 5-10 natural language expressions that describe:
1. What the table represents (its purpose/domain)
2. What types of entities/records it stores
3. Key relationships between columns
4. What business questions this table could help answer
5. Notable patterns or constraints in the data structure

Here is the SQL table in markdown format:

{input.sql_table_markdown}

Please return only the natural language expressions as a numbered list, one per line, without any additional explanation or formatting."""

    message = Message.user(content)
    params = ChatParams(max_tokens=512)
    response = csi.chat("llama-3.1-8b-instruct", [message], params)
    
    # Parse the response to extract individual expressions
    response_text = response.message.content or ""
    expressions = []
    
    for line in response_text.strip().split('\n'):
        line = line.strip()
        # Remove numbering if present (e.g., "1. ", "2. ", etc.)
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
            # Find the first space after numbering and take the rest
            parts = line.split(' ', 1)
            if len(parts) > 1:
                expressions.append(parts[1].strip())
        elif line:  # Non-numbered line
            expressions.append(line)
    
    # Filter out empty expressions
    expressions = [expr for expr in expressions if expr]
    
    return Output(natural_language_expressions=expressions)
