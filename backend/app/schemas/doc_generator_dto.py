import uuid

from pydantic import BaseModel, ConfigDict


class DocGenerationRequest(BaseModel):
    target_file: str # e.g. user_service.py, UserService.java, README.md
    code_content: str
    doc_type: str = "docstring" # docstring, javadoc, readme, api_doc, missing_comments, function_description, usage_examples
    pull_request_id: uuid.UUID | None = None


class GeneratedDocItem(BaseModel):
    id: uuid.UUID | None = None
    pull_request_id: uuid.UUID | None = None
    doc_type: str
    doc_title: str | None = None
    target_file: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class DocGeneratorResponse(BaseModel):
    doc_id: uuid.UUID
    doc_type: str
    doc_title: str
    target_file: str
    content: str
    download_url: str
