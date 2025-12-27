from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Literal

class PromptIn(BaseModel):
    """Schema for creating a new prompt."""
    prompt_name: str
    prompt_content: str

class EditPromptIn(BaseModel):
    """Schema for editing an existing prompt."""
    prompt_content: str   

class EvalCaseIn(BaseModel):
    """Schema for an evaluation test case input."""
    query: str
    correct_answer: str

class EvalOut(BaseModel):
    """Schema for the evaluation api output."""
    prompt_content: str = Field(description="Old or fixed prompt after evaluation result.")
    quality: Literal["pass", "fail"] = Field(description="Overall quality evaluation result.")
    reason: str = Field(description="Explanation for the evaluation decision.")

class PromptOut(BaseModel):
    prompt_id: UUID
    prompt_name: str
    current_version_id: UUID

    model_config = ConfigDict(from_attributes=True)

class DisplayPrompt(BaseModel):
    """Schema for displaying prompt with its current version details."""
    prompt_id: UUID
    current_version_id: UUID
    version_number: int
    prompt_name: str
    prompt_content: str
    status: str

class TestCaseIn(BaseModel):
    """Test case input schema."""
    question: str
    answer: str
    prompt_id: UUID 

class TestCaseOut(BaseModel):
    """Test Case output schema."""
    test_id: UUID
    question: str
    answer: str
    prompt_id: UUID 

    model_config = ConfigDict(from_attributes=True)
 
class EvaluationLLMOut(BaseModel):
    """Structured response from the evaluator llm inside the evaluate_prompt tool."""
    faithfulness: float = Field(description="Score how strictly the RAG Answer is grounded in the Provided Context.")
    context_relevancy: float = Field(description="Score how useful and relevant the Provided Context is for answering the User Query.")
    answer_relevancy: float = Field(description=" Score how well the RAG Answer addresses the User Query compared to the Correct Answer.")
    reason: str

class EvaluateToolInput(BaseModel):
    """Input for the evaluate_prompt tool."""
    prompt_content: str = Field(description="The instruction or prompt used to generate the RAG answer.")
    query: str = Field(description="The original user question.")
    rag_ans: str = Field(description="The answer produced by the RAG system.")
    correct_answer: str = Field(description="The expected or gold-standard answer.")
    context: str = Field(description="The retrieved or supporting context provided to the RAG system.")

class UpdateToolInput(BaseModel):
    """Input for the update tool."""
    # Context for the tool
    prompt_content: str = Field(description="The instruction or prompt used to generate the RAG answer.")
    query: str = Field(description="The original user question.")
    rag_ans: str = Field(description="The answer produced by the RAG system.")
    correct_answer: str = Field(description="The expected or gold-standard answer.")
    context: str = Field(description="The retrieved or supporting context provided to the RAG system.")

    # Metrics from the evaluation
    faithfulness: float = Field(description="Faithfulness score from evaluation.")
    context_relevancy: float = Field(description="Context Relevancy score from evaluation.")
    answer_relevancy: float = Field(description="Answer Relevancy score from evaluation.")

    # Output from the evaluation  
    quality: Literal["pass", "fail"] = Field(description="Overall quality evaluation result.")
    reason: str = Field(description="Explanation for the evaluation decision.")

class UpdateLLMOut(BaseModel):
    """Response from the update_prompt tool."""
    updated_prompt: str = Field(description="The refined prompt content after applying updates.")

class AgentResponse(BaseModel):
    """Response from the EvaluatorAgent."""
    quality: Literal["pass", "fail"] = Field(description="Overall quality evaluation result.")
    prompt_content: str = Field(description="The updated prompt content if quality is 'fail', else existing prompt.")
    reason: str = Field(description="Explanation for the evaluation decision.")

