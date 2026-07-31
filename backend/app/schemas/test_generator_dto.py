import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TestGenerationRequest(BaseModel):
    target_file: str # e.g. src/auth/user_service.py or UserService.java
    code_content: str
    test_framework: str = "pytest" # pytest, junit, jest
    test_category: str = "comprehensive" # positive, negative, boundary, mock, comprehensive
    pull_request_id: Optional[uuid.UUID] = None


class GeneratedTestItem(BaseModel):
    id: Optional[uuid.UUID] = None
    pull_request_id: Optional[uuid.UUID] = None
    test_framework: str
    test_category: str
    test_name: str
    target_file: str
    generated_code: str
    workflow_explanation: str
    is_passing: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class TestGeneratorResponse(BaseModel):
    test_id: uuid.UUID
    test_framework: str
    test_category: str
    test_name: str
    target_file: str
    generated_code: str
    workflow_explanation: str
    download_url: str
    is_passing: Optional[bool] = None
