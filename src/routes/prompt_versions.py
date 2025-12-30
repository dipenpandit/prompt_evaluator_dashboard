from fastapi import APIRouter, Depends, status, HTTPException
from src.schemas import DisplayVersion
from src.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.db.models import Prompt, PromptVersion
from typing import List
from src.services.update_prompt import set_prompt_active
from uuid import UUID

router = APIRouter(prefix="/versions", tags=["Prompt Versions"])

# GET - /versions/{prompt_id}
@router.get("/{prompt_id}", response_model=List[DisplayVersion], status_code=status.HTTP_200_OK)
async def get_prompt_versions(prompt_id: UUID, db: Session = Depends(get_db)) -> List[DisplayVersion]:
    """Retrieve all versions of a specific prompt by its id."""
    prompt = db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    
    query = (
        select(
            PromptVersion
        ).where(PromptVersion.prompt_id == prompt.prompt_id)
    )
    versions = db.execute(query).scalars().all()
    if not versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No versions found for this prompt")
    return [
        DisplayVersion.model_validate(version) for version in versions
    ]


# GET - /versions/version/{version_id}
@router.get("/version/{version_id}", response_model=DisplayVersion, status_code=status.HTTP_200_OK)
async def get_prompt_version_by_id(version_id: UUID, db: Session = Depends(get_db)) -> DisplayVersion:
    """Retrieve a specific prompt version by its version id."""
    version = db.get(PromptVersion, version_id)
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt version not found")
    return DisplayVersion.model_validate(version)


# PATCH - /versions/{version_id}/activate
@router.patch("/{version_id}/activate", response_model=DisplayVersion, status_code=status.HTTP_200_OK)
async def activate_prompt_version(version_id: UUID,
                                  db: Session = Depends(get_db)) -> DisplayVersion:
    """Set a specific prompt version as the active version for its parent prompt."""
    updated_version = set_prompt_active(version_id, db)
    return DisplayVersion.model_validate(updated_version)
