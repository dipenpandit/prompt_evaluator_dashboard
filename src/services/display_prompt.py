from fastapi import Depends, status, HTTPException
from src.schemas import DisplayPrompt
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from typing import List
from sqlalchemy import select


def display_prompt(prompt: Prompt, db: Session = Depends(get_db)) -> DisplayPrompt:
    """Retrieve full prompt details including its current version."""
    
    # Get current version of prompt
    current_version = db.get(PromptVersion, prompt.current_version_id)
    if not current_version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt version not found")
    
    display_data = DisplayPrompt(
        prompt_id=prompt.prompt_id,
        current_version_id=prompt.current_version_id,
        prompt_name=prompt.prompt_name,
        version_number=current_version.version_number,
        prompt_content=current_version.prompt_content,
        status=current_version.status
    )
    return display_data 


def display_all_prompts(db: Session = Depends(get_db)) -> List[DisplayPrompt]:
    """Retrieve all prompts with their current version details."""

    #  Get full prompt details of latest prompt version
    stmt = (
        select(
            Prompt.prompt_id,
            Prompt.current_version_id,
            Prompt.prompt_name,
            PromptVersion.version_number,
            PromptVersion.prompt_content,
            PromptVersion.status
        )   
        .join(
            PromptVersion,
            Prompt.current_version_id == PromptVersion.version_id
        )
    )

    result = db.execute(stmt).all()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prompts found")
    
    prompts = [
        DisplayPrompt(
            prompt_id=row.prompt_id,
            current_version_id=row.current_version_id,
            version_number=row.version_number,
            prompt_name=row.prompt_name,
            prompt_content=row.prompt_content,
            status=row.status,
        )
        for row in result
    ]

    return prompts