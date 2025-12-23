from fastapi import APIRouter, Depends, status
from ..schemas import PromptIn, PromptOut
from ..db.database import get_db
from sqlalchemy.orm import Session
from ..db.models import Prompt

router = APIRouter(prefix="/prompts", tags=["Create Prompt"])

@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def check_prompt(prompt: PromptIn,
                       db: Session = Depends(get_db)) -> PromptOut:
    new_prompt = Prompt(**prompt.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)  # refresh to fetch default values properly like the timestamp 
    return new_prompt



