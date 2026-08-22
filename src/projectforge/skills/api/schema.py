from pydantic import BaseModel, Field

class RequestResponseField(BaseModel):
    name: str
    type: str
    required: bool
    description: str

class ErrorResponse(BaseModel):
    status_code: int
    error_code: str
    description: str

class Endpoint(BaseModel):
    path: str
    method: str
    summary: str
    description: str
    auth_required: bool
    request_headers: list[str] = []
    request_query_params: list[RequestResponseField] = []
    request_body: list[RequestResponseField] = []
    response_body: list[RequestResponseField] = []
    error_responses: list[ErrorResponse] = []

class APIOutput(BaseModel):
    api_style: str
    style_rationale: str
    base_path: str
    authentication_strategy: str
    rate_limiting_notes: str
    endpoints: list[Endpoint] = Field(min_length=1)
