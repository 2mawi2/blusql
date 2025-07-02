from pharia_skill import ChatParams, Csi, Message, skill
from pydantic import BaseModel


class Input(BaseModel):
    user_question: str
    sql_table_markdown: str


class Output(BaseModel):
    natural_language_expressions: list[str]


@skill
def sql_to_natural_language(csi: Csi, input: Input) -> Output:
    content = f"""You are an expert in SQL and natural language processing. Your task is to analyze the given SQL table structure and answer the user's question, then provide relevant insights.

User Question: {input.user_question}

SQL Table Structure:
{input.sql_table_markdown}

Please provide a response that:
1. First answers the user's question based on what can be determined from the table structure
2. Then provides 2-5 additional insights about the table that are relevant to the user's question

Focus on being concise and relevant. Return only the numbered responses, one per line, without additional formatting."""

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
