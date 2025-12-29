from fastapi import APIRouter, Depends, status, HTTPException
from src.schemas import PromptIn, PromptOut, DisplayPrompt, EditPromptIn
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from typing import List
from src.services.display_prompt import display_all_prompts, display_prompt
from src.services.update_prompt import update_prompt_version, set_prompt_active

router = APIRouter(prefix="/prompts", tags=["Prompts"])

# POST - /prompts/
@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt_data: PromptIn, db: Session = Depends(get_db)):
    """Create a new prompt along with its initial version.
    1. Create a new prompt_id in the prompts table
    2. Create a new version in the prompt_versions table linked to that prompt_id
    3. Set the current_version_id in the prompts table to the newly created version_id
    4. Commit all changes to the database at once
    """
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

# GET - /prompts/
@router.get("/", response_model=List[DisplayPrompt], status_code=status.HTTP_200_OK)
async def get_prompts(db: Session = Depends(get_db)) -> List[DisplayPrompt]:
    """Retrieve all prompts with their current version details."""
    return display_all_prompts(db) 


# GET - /prompts/{prompt_id}
@router.get("/{prompt_id}", response_model=DisplayPrompt, status_code=status.HTTP_200_OK)
async def get_prompt_by_id(prompt_id: str, db: Session = Depends(get_db)) -> DisplayPrompt:
    """Retrieve a specific prompt by its ID along with its current version details."""
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return display_prompt(prompt, db)

# PUT - /prompts/{prompt_id}
@router.put("/{prompt_id}", response_model=DisplayPrompt, status_code=status.HTTP_201_CREATED)
async def update_prompt(prompt_id: str, 
                        prompt_data: EditPromptIn,
                        db: Session = Depends(get_db)) -> DisplayPrompt:
 

    # Fetch the current prompt (row) to get its current version number
    current_prompt = db.get(Prompt, prompt_id)
    if not current_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    return update_prompt_version(current_prompt, prompt_data, db)


# PATCH - /prompts/{prompt_id}/activate
@router.patch("/{prompt_id}/activate", response_model=DisplayPrompt, status_code=status.HTTP_200_OK)
async def activate_prompt(prompt_id: str,
                          db: Session = Depends(get_db)) -> DisplayPrompt:
    """Set the current version of the prompt to active status."""
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    return set_prompt_active(prompt, db)