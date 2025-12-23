from fastapi import FastAPI
from .routes import create_prompt
from .db.models import Base
from .db.database import engine

app = FastAPI() 

Base.metadata.create_all(bind=engine)

# app.include_router(ingest.router)
app.include_router(create_prompt.router)

