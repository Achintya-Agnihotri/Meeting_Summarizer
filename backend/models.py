from typing import Annotated
from pydantic import BaseModel, Field, field_validator

NotBlank = Annotated[str, Field(min_length=1)]

class ActionItem(BaseModel):
    task: NotBlank
    owner: str | None = None
    deadline: str | None = None

    @field_validator("task", "owner", "deadline", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return value.strip() or None if isinstance(value, str) else value

    @field_validator("task")
    @classmethod
    def task_must_not_be_empty(cls, value: str | None) -> str:
        if not value:
            raise ValueError("Action item task cannot be blank")
        return value

class MeetingAnalysis(BaseModel):
    summary: NotBlank
    key_decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

class MeetingResult(MeetingAnalysis):
    transcript: NotBlank

class HealthResponse(BaseModel):
    status: str
