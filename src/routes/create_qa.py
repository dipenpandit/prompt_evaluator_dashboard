from fastapi import APIRouter, Depends, status
from src.schemas import TestCaseIn, TestCaseOut, UpdatePromptIn
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import TestCase

router = APIRouter(prefix="/ques_ans", tags=["Question Answers"])

@router.post("/", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
async def create_ques(qa: TestCaseIn,
                    db: Session = Depends(get_db)) -> TestCaseOut:
    new_qa = TestCase(**qa.model_dump())
    db.add(new_qa)
    db.commit()
    db.refresh(new_qa)  
    return new_qa

@router.get("/", response_model=list[TestCaseOut], status_code=status.HTTP_200_OK)
async def get_ques(db: Session = Depends(get_db)) -> list[TestCaseOut]:
    qas = db.query(TestCase).all()
    return qas

