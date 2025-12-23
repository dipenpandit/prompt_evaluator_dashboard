from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class PromptIn(BaseModel):
    prompt_name: str
    version: str 
    prompt_content: str

class PromptOut(BaseModel):
    prompt_id: UUID
    prompt_name: str
    version: str 
    prompt_content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class TestCaseIn(BaseModel):
    question: str
    answer: str

class TestCaseOut(BaseModel):
    test_id: UUID
    question: str
    answer: str
    prompt_id: str 

    model_config = ConfigDict(from_attributes=True)
 
 
