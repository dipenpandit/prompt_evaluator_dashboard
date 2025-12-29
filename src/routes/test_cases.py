from fastapi import APIRouter, Depends, status, HTTPException
from src.schemas import TestResultOut, TestCaseOut, DisplayTestResult
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import TestResults, TestCase
from uuid import UUID
from sqlalchemy import select
from typing import List

router = APIRouter(prefix="/test_cases", tags=["Test Cases"])

# GET /{prompt_id}
@router.get("/{prompt_id}", response_model=list[TestCaseOut], status_code=status.HTTP_200_OK)
async def get_test_cases_by_id(prompt_id: UUID, db: Session = Depends(get_db)) -> list[TestCaseOut]:
    stmt = select(TestCase).where(TestCase.prompt_id == prompt_id)
    result = db.execute(stmt).scalars().all()
    return result

# GET /{prompt_id}/{version_id}/results
@router.get("/{prompt_id}/{version_id}/results", response_model=List[TestResultOut], status_code=status.HTTP_200_OK)
async def get_test_results_by_prompt_version(prompt_id: UUID, version_id: UUID, db: Session = Depends(get_db)) -> List[TestResultOut]:
    stmt = (
        select(
            TestCase.test_id,
            TestCase.question,
            TestCase.answer,
            TestResults.result,
            TestResults.reason
        ).join(
            TestResults,
            TestCase.test_id == TestResults.test_id
        ).where(
            TestCase.prompt_id == prompt_id,
            TestResults.prompt_version_id == version_id
        )
    )
    result = db.execute(stmt).all()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No results found")
    
    return [
        DisplayTestResult(
            test_id=row.test_id,
            question=row.question,
            answer=row.answer,
            result=row.result,
            reason=row.reason
        ) for row in result
    ]

