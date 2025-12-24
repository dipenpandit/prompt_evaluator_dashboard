from fastapi import APIRouter, Depends, status
from src.schemas import PromptIn, PromptOut, DisplayPrompt
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from typing import List
from sqlalchemy import select

router = APIRouter(prefix="/prompts", tags=["Create Prompt"])

# POST
@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt_data: PromptIn, db: Session = Depends(get_db)):
    # Create the Parent container first
    new_prompt = Prompt(prompt_name=prompt_data.prompt_name)
    db.add(new_prompt)
    db.flush() # This generates the new_prompt.prompt_id UUID

    # Create the Version linked to that ID
    new_version = PromptVersion(
        prompt_id=new_prompt.prompt_id,
        prompt_content=prompt_data.prompt_content,
        version_number=1
    )
    db.add(new_version)
    db.flush() # This generates the new_version.version_id UUID

    # 3. Point the Parent to the New Version
    new_prompt.current_version_id = new_version.version_id
    
    db.commit() # Now everything is saved at once!
    db.refresh(new_prompt)
    return new_prompt

# GET
@router.get("/", response_model=List[DisplayPrompt], status_code=status.HTTP_200_OK)
async def get_prompts(db: Session = Depends(get_db)) -> List[DisplayPrompt]:
    stmt = (
        select(
            Prompt.prompt_id,
            PromptVersion.version_number,
            PromptVersion.prompt_name,
            PromptVersion.prompt_content,
            PromptVersion.status
        )
        .join(
            PromptVersion,
            Prompt.current_version_id == PromptVersion.version_id
        )
    )

    result = db.execute(stmt).all()

    prompts = [
        DisplayPrompt(
            prompt_id=row.prompt_id,
            version_number=row.version_number,
            prompt_name=row.prompt_name,
            prompt_content=row.prompt_content,
            status=row.status,
        )
        for row in result
    ]

    return prompts


# PUT
