from sqlalchemy.orm import Session 
from src.schemas import TestCaseIn, TestCaseOut, TestResultIn, TestResultOut
from src.db.models import TestCase, TestResults
from src.db.database import get_db
from fastapi import Depends
from uuid import UUID

def add_test_case(test_case: TestCaseIn,
                  prompt_id: UUID,
                  db: Session = Depends(get_db)) -> TestCaseOut:
    new_test_case = TestCase(**test_case.model_dump(), prompt_id=prompt_id)
    db.add(new_test_case)
    db.commit()
    db.refresh(new_test_case)  
    return TestCaseOut.model_validate(new_test_case)


def add_result(test_result: TestResultIn,
               db: Session = Depends(get_db)) ->TestResultOut:
    new_result = TestResults(**test_result.model_dump())
    db.add(new_result)
    db.commit()
    db.refresh(new_result)  
    return TestResultOut.model_validate(new_result) 

