from fastapi import APIRouter, Depends, HTTPException, Request

from service.dependencies import get_token, with_kernel
from service.kernel import Json, Kernel, KernelException, Skill
from service.models import HealthResponse
from service.extract_schema import get_db_context
from pydantic import BaseModel
from typing import Optional

router: APIRouter = APIRouter()
        
class Input(BaseModel):
    natural_query: str
    schema: Optional[str] = None

class SqlToNlInput(BaseModel):
    user_question: str
    sql_result_markdown: str


class Output(BaseModel):
    natural_language_response: str


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/generate-bluesql")
async def qa(
    request: Request,
    token: str = Depends(get_token),
    kernel: Kernel = Depends(with_kernel),
) -> Json:
    generate_sql_skill = Skill(namespace="customer-playground", name="generate-bluesql")
    sql_to_nl_skill = Skill(namespace="customer-playground", name="sql_to_nl")

    try:
        request = await request.json()
        context = get_db_context()
        request["db_context"] = {
            "db_technology": context.db_technology,
            "schema": context.schema
        }
        response = await kernel.run(generate_sql_skill, token, request)

        sql_result_markdown="""
        USER 1 Marius
        USER 2 Gustav
        """

        sqlToNlInput = SqlToNlInput(
            user_question=request["natural_query"],
            sql_result_markdown=sql_result_markdown
        )

        nl_response = await kernel.run(sql_to_nl_skill, token, sqlToNlInput.model_dump())
        response["explanation"] = nl_response["natural_language_response"]
        return response
            
    except KernelException as exp:
        error_message = ",".join(exp.args)
        if error_message.startswith(
            "Sorry, We could not find the skill you requested in its namespace"
        ):
            error_message += "\n\nPlease check https://docs.aleph-alpha.com/products/pharia-ai/pharia-studio/tutorial/pharia-applications-quick-start/#phariaai-application-skill for instructions on deploying the skill"
        print(error_message)
        raise HTTPException(exp.status_code, error_message) from exp


@router.post("/sql-to-nl")
async def sql_to_nl(
    request: Request,
    token: str = Depends(get_token),
    kernel: Kernel = Depends(with_kernel),
) -> Json:
    skill = Skill(namespace="customer-playground", name="sql_to_nl")
    try:
        response = await kernel.run(skill, token, await request.json())
        return response
    except KernelException as exp:
        error_message = ",".join(exp.args)
        if error_message.startswith(
            "Sorry, We could not find the skill you requested in its namespace"
        ):
            error_message += "\n\nPlease check https://docs.aleph-alpha.com/products/pharia-ai/pharia-studio/tutorial/pharia-applications-quick-start/#phariaai-application-skill for instructions on deploying the skill"
        print(error_message)
        raise HTTPException(exp.status_code, error_message) from exp

        
