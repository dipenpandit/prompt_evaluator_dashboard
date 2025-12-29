from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 
from sqlalchemy import ForeignKey, String, UUID, DateTime
from typing import List, Optional 
import datetime
from uuid import uuid4

class Base(DeclarativeBase):
    pass


class Prompt(Base):
    __tablename__ = "prompts"

    prompt_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    prompt_name: Mapped[str] = mapped_column(String, nullable=False)
    current_version_id: Mapped[UUID] = mapped_column(ForeignKey("prompt_versions.version_id"), nullable=True)

class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    version_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.prompt_id"), nullable=False)
    version_number: Mapped[int] = mapped_column(default=1)
    prompt_content: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="inactive")
    created: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class TestCase(Base):
    __tablename__ = "test_cases"
    
    test_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    question: Mapped[str] = mapped_column(String, nullable=True)
    answer: Mapped[str] = mapped_column(String, nullable=True)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.prompt_id"), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))


class TestResults(Base):
    __tablename__ = "test_results"
    
    result_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    test_id: Mapped[UUID] = mapped_column(ForeignKey("test_cases.test_id"), nullable=False)
    prompt_version_id: Mapped[UUID] = mapped_column(ForeignKey("prompt_versions.version_id"), nullable=False)
    result: Mapped[str] = mapped_column(String, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)

