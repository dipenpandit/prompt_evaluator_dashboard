from fastapi import APIRouter, Depends, status
from ..schemas import TestCaseOut
router = APIRouter(prefix="/ques_ans", tags=["Questino Answers"])

# @router.post("/", response_format=TestCaseOut)