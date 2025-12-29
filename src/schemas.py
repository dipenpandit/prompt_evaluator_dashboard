from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Literal, Optional

class PromptIn(BaseModel):
    """Schema for creating a new prompt."""
    prompt_name: str = Field(description="The name of the prompt.")
    prompt_content: str = Field(description="The content of the prompt.")

class EditPromptIn(BaseModel):
    """Schema for editing an existing prompt."""
    prompt_content: str = Field(description="The updated content of the prompt.")


class PromptOut(BaseModel):
    prompt_id: UUID = Field(description="The unique identifier of the prompt.")
    prompt_name: str = Field(description="The name of the prompt.")
    current_version_id: UUID = Field(description="The current version identifier of the prompt.")

    model_config = ConfigDict(from_attributes=True)

class DisplayPrompt(BaseModel):
    """Schema for displaying prompt with its current version details."""
    prompt_id: UUID = Field(description="The unique identifier of the prompt.")
    current_version_id: UUID = Field(description="The current version identifier of the prompt.")
    version_number: int = Field(description="The version number of the prompt.")
    prompt_name: str = Field(description="The name of the prompt.")
    prompt_content: str = Field(description="The content of the prompt.")
    status: str = Field(description="The status of the prompt version.")

class TestCaseIn(BaseModel):
    """Test case input schema."""
    question: str = Field(description="The question for the test case.")
    answer: str = Field(description="The expected answer for the test case.")

class TestCaseOut(BaseModel):
    """Test Case output schema."""
    test_id: UUID = Field(description="The unique identifier of the test case.")
    question: str = Field(description="The question for the test case.")
    answer: str = Field(description="The expected answer for the test case.")
    prompt_id: UUID = Field(description="The prompt associated with the test case.")
    created: datetime = Field(description="The creation timestamp of the test case.")

    model_config = ConfigDict(from_attributes=True)


class TestResultIn(BaseModel):
    """Test Result input schema."""
    test_id: UUID = Field(description="The test case being evaluated.")
    prompt_version_id: UUID = Field(description="The version of the prompt being tested.")
    result: str = Field(description="Result of the test case evaluation.")
    reason: str = Field(description="Explanation for the test result.")

class TestResultOut(BaseModel):
    """Test Result output schema."""
    result_id: UUID = Field(description="The test case being evaluated.")
    test_id: UUID = Field(description="The test case being evaluated.")
    prompt_version_id: UUID = Field(description="The version of the prompt being tested.")
    result: str = Field(description="Result of the test case evaluation.")
    reason: str = Field(description="Explanation for the test result.")
    new_prompt_content: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class DisplayTestResult(BaseModel):
    """Schema for displaying test result with test case details."""
    test_id: UUID = Field(description="The unique identifier of the test case.")
    question: str = Field(description="The question for the test case.")
    answer: str = Field(description="The expected answer for the test case.")
    result: str = Field(description="Result of the test case evaluation.")
    reason: str = Field(description="Explanation for the test result.")

 
### Schemas for Evaluator Agent Interaction
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

