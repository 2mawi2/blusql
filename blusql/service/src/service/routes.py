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

@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/generate-bluesql")
async def qa(
    request: Request,
    token: str = Depends(get_token),
    kernel: Kernel = Depends(with_kernel),
) -> Json:
    skill = Skill(namespace="customer-playground", name="generate-bluesql")
    try:
        request = await request.json()
        context = get_db_context()
        request["schema"] = str(context)
        response = await kernel.run(skill, token, request)
        return response
    except KernelException as exp:
        error_message = ",".join(exp.args)
        if error_message.startswith(
            "Sorry, We could not find the skill you requested in its namespace"
        ):
            error_message += "\n\nPlease check https://docs.aleph-alpha.com/products/pharia-ai/pharia-studio/tutorial/pharia-applications-quick-start/#phariaai-application-skill for instructions on deploying the skill"
        print(error_message)
        raise HTTPException(exp.status_code, error_message) from exp
