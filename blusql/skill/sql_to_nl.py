from pharia_skill import ChatParams, Csi, Message, skill
from pydantic import BaseModel


class Input(BaseModel):
    user_question: str
    sql_result_markdown: str


class Output(BaseModel):
    natural_language_response: str


@skill
def sql_to_natural_language(csi: Csi, input: Input) -> Output:
    content = f"""You are a business analyst. Analyze the SQL query results and provide a concise summary.

User Question: {input.user_question}

SQL Query Results:
{input.sql_result_markdown}

Provide a brief response (2-3 sentences max) that:
1. Directly answers the question with key numbers/insights
2. Identifies the most important pattern or trend
3. Suggests one actionable next step

Be concise and business-focused. Avoid filler words and repetition."""

    message = Message.user(content)
    params = ChatParams(max_tokens=150)
    response = csi.chat("llama-3.1-8b-instruct", [message], params)
    
    # Return the response directly as a single string
    response_text = response.message.content or "I couldn't analyze the table structure for your question."
    
    return Output(natural_language_response=response_text.strip())
