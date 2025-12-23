from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 
from sqlalchemy import ForeignKey, String, UUID, DateTime
from typing import List, Optional 
import datetime
from uuid import uuid4

class Base(DeclarativeBase):
    pass

class Prompt(Base):
    __tablename__ = "prompts"
    
    prompt_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), 
                                            primary_key=True, index=True,
                                            default=uuid4)
    prompt_name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    prompt_content: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

class TestCase(Base):
    __tablename__ = "test_cases"
    
    test_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String, nullable=True)
    answer: Mapped[str] = mapped_column(String, nullable=True)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.prompt_id"), nullable=False)