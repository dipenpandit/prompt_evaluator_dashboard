from fastapi import FastAPI
from src.routes import prompt_versions, prompts, test_cases, evaluation
from src.db.models import Base
from src.db.database import engine

app = FastAPI() 

Base.metadata.create_all(bind=engine)

app.include_router(prompts.router)
app.include_router(test_cases.router)
app.include_router(prompt_versions.router)
app.include_router(evaluation.router)


