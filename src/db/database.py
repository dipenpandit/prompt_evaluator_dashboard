from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from src.config import settings

# postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{port}/{db_name}
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@{settings.db_host}:5432/{settings.db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try: 
        yield db 
    finally:
        db.close()  # always close db 

