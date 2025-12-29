from fastapi import Depends, HTTPException
from src.schemas import DisplayPrompt, EditPromptIn, DisplayVersion
from src.db.database import get_db
from sqlalchemy.orm import Session
from src.db.models import Prompt, PromptVersion
from uuid import UUID

# Manual Edit or LLM Generated prompt update service
def update_prompt_version(prompt: Prompt,
                          prompt_data: EditPromptIn,
                          db: Session = Depends(get_db)) -> DisplayPrompt:
    """Create a new version of the prompt with the updated prompt content.
    1. Fetch the current prompt to get its current version number
    2. Create a new PromptVersion with version_number incremented by 1
    3. Update the current_version_id in the parent Prompt to point to the new version.
    4. Commit all the changes to the database at once"""
    
    # Create new version
    latest_version = db.get(PromptVersion, prompt.current_version_id)
    if not latest_version:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    new_version_number = latest_version.version_number + 1


    new_version = PromptVersion(
        prompt_id=prompt.prompt_id,
        prompt_content=prompt_data.prompt_content,
        version_number=new_version_number
    )
    db.add(new_version)
    db.flush()  # Generates new_version.version_id

    # 3. Update prompt to point to new version
    prompt.current_version_id = new_version.version_id

    db.commit()  # Save all changes at once
    db.refresh(prompt)
    return DisplayPrompt(
        prompt_id=prompt.prompt_id,
        prompt_name=prompt.prompt_name,
        current_version_id=prompt.current_version_id,
        prompt_content=new_version.prompt_content,
        version_number=new_version.version_number,
        status=new_version.status
    )


# Set prompt version to active service
def set_prompt_active(version_id: UUID,
                      db: Session = Depends(get_db)):
    """Set the current version of the prompt to active status."""
    version = db.get(PromptVersion, version_id)
    if version.status != "active":
        version.status = "active"
        db.commit()
    return DisplayVersion(
        version_id=version.version_id,
        prompt_id=version.prompt_id,
        prompt_content=version.prompt_content,
        version_number=version.version_number,
        status=version.status,
        created_at=version.created_at
    )



