from fastapi import APIRouter, Depends, status, HTTPException
from src.schemas import TestCaseIn, TestCaseOut
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import TestCase
from uuid import UUID
from sqlalchemy import select
from typing import List
from src.services.add_test_case import add_test_case

router = APIRouter(prefix="/test_cases", tags=["Test Cases"])

# GET - /{prompt_id}
@router.get("/{prompt_id}", response_model=List[TestCaseOut], status_code=status.HTTP_200_OK)
async def get_test_cases_by_id(prompt_id: UUID, db: Session = Depends(get_db)) -> List[TestCaseOut]:
    stmt = select(TestCase).where(TestCase.prompt_id == prompt_id)
    result = db.execute(stmt).scalars().all()
    return [
        TestCaseOut.model_validate(tc) for tc in result
    ]


# GET - /{test_id} 
@router.get("/{test_id}", response_model=TestCaseOut, status_code=status.HTTP_200_OK)
async def get_test_case_by_id(test_id: UUID, db: Session = Depends(get_db)) -> TestCaseOut:
    test_case = db.get(TestCase, test_id)
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    return TestCaseOut.model_validate(test_case) 


# POST - /{prompt_id}
@router.post("/{prompt_id}", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
async def create_test_case(prompt_id: UUID, test_case: TestCaseIn, db: Session = Depends(get_db)) -> TestCaseOut:
    test_case_obj = add_test_case(test_case, prompt_id, db)
    return TestCaseOut.model_validate(test_case_obj) 


# PUT -/{test_id}
@router.put("/{test_id}", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
async def update_test_case(test_id: UUID, updated_data: TestCaseIn, db: Session = Depends(get_db)) -> TestCaseOut:
    test_case = db.get(TestCase, test_id)
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    
    test_case.question = updated_data.question
    test_case.answer = updated_data.answer
    
    db.commit()
    db.refresh(test_case)
    return TestCaseOut.model_validate(test_case) 


# DELETE - /{test_id}
@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(test_id: UUID, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, test_id)
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    
    db.delete(test_case)
    db.commit()
    return None  # good practice to return None for 204 responses 

