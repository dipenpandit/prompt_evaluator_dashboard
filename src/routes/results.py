from fastapi import APIRouter, Depends, status, HTTPException
from src.schemas import Disp, DisplayTestResult
from src.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.db.models import TestResults, TestCase
from typing import List
from src.schemas import TestResultOut

router = APIRouter(prefix="/results", tags=["Results"])

# GET - /results/{version_id}
@router.get("/{version_id}", response_model=List[TestResultOut], status_code=status.HTTP_200_OK)
async def get_results_by_version_id(version_id: str, db: Session = Depends(get_db)) -> List[TestResultOut]:
    """Retrieve all test results for a specific prompt version"""
    stmt = (
        select(
            TestCase.test_id,
            TestResults.prompt_version_id,
            TestCase.question,
            TestCase.answer,
            TestResults.result,
            TestResults.reason
        ).join(
            TestResults,
            TestCase.test_id == TestResults.test_id
        ).where(
            TestResults.prompt_version_id == version_id
        )
    )
    result = db.execute(stmt).all()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No results found")

    return [
        DisplayTestResult(
            test_id=row.test_id,
            prompt_version_id=row.prompt_version_id,
            question=row.question,
            answer=row.answer,
            result=row.result,
            reason=row.reason
        ) for row in result
    ]
