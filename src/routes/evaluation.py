from fastapi import APIRouter, status, Depends, HTTPException
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.schemas import EvalOut, EvalCaseIn
from src.db.models import Prompt, PromptVersion
from src.config import settings
from src.evaluator.agent import EvaluatorAgent, agent
import requests 
import re
import json

router = APIRouter(prefix="/eval", tags=["Evaluation"])

# POST
@router.post("/{prompt_id}", response_model=EvalOut, status_code=status.HTTP_200_OK)
async def make_evaluation(prompt_id: str,
                          query: EvalCaseIn, 
                          db: Session = Depends(get_db),
                          agent: EvaluatorAgent = Depends(lambda: agent)): 
    """Evaluate the prompt based on the retrieved answer and context from RAG and update the prompt content if necessary (quality: bad)
       1. Get the prompt content from the database
       2. Call RAG API with the provided query
       3. Pass prompt_content, query, rag_ans, correct_answer, context to agent to evaluate the prompt
       4. If the quality is "fail" and a fixed prompt_content is provided, update the prompt in the database and set it active
       5. If the quality is "pass", set the prompt status to active"""
    
    # Get the prompt content from the database
    prompt = db.get(Prompt, prompt_id)  
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    current_version = db.get(PromptVersion, prompt.current_version_id) 
    prompt_content = current_version.prompt_content

    # Call RAG API
    rag_response = requests.post(f"{settings.rag_api}", json={"query": query.query})
    
    if rag_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG API error, check your api url and server status")
    
    rag_data = rag_response.json()

    # Context for agent to evaluate prompt
    rag_ans = rag_data.get("answer", "")
    rag_context = rag_data.get("context", "")
    correct_answer = query.correct_answer

    # Pass prompt_content, query, rag_ans, correct_answer, context to agent
    agent_result = agent.evaluate(
        prompt_content=prompt_content,
        query=query.query,
        rag_ans=rag_ans,
        correct_answer=correct_answer,
        context=rag_context
    )

    if not agent_result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Evaluator Agent failed to provide a response.")
        
    # Parse the agent response to extract JSON
    match = re.search(r'\{.*\}', agent_result)
    if match:
        json_str = match.group(0)  # still a string
        agent_json = json.loads(json_str) # convert to dictionary

    if agent_json.get("quality") == "fail":
         print(agent_json.keys())
        # Add the updated prompt to the databse with status active and set the current version in prompts table to the new version
         update_response = requests.put(
             f"{settings.api_url}/prompts/{prompt_id}",
             json={
                    "prompt_content": agent_json.get("prompt_content", ""),
                })
         print(update_response.json())
         if update_response.status_code != 201:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update prompt after evaluation.")
         
        #  Set the status of the new version to active for the updated prompt
         activate_status = requests.patch(f"{settings.api_url}/prompts/{prompt_id}/activate")
         if activate_status.status_code != 200:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate updated prompt after evaluation.")
         print(activate_status.json())
    elif agent_json.get("quality", "") == "pass":
        print(f"Elif keys, {agent_json.keys()}")
        # Set the status of the passed prompt to active
        activate_status = requests.patch(f"{settings.api_url}/prompts/{prompt_id}/activate")
        if activate_status.status_code != 200:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate prompt after evaluation.")


    return EvalOut(
        prompt_content = agent_json.get("prompt_content", ""),
        quality = agent_json.get("quality", ""),
        reason= agent_json.get("reason", ""),
    )