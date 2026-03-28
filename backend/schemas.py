from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CandidateSubmission(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    education: str = Field(min_length=1, max_length=200)
    experience: float = Field(ge=0, le=60)
    projects: str = Field(min_length=1)
    github_url: HttpUrl

    @field_validator("name", "education", "projects")
    @classmethod
    def strip_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field cannot be empty")
        return normalized


class JobCreateResponse(BaseModel):
    job_id: str


class StepUpdate(BaseModel):
    step: str
    status: str
    timestamp: str


class InterviewQuestion(BaseModel):
    question: str
    focus_area: str
    difficulty: str
    why_this_question: str | None = None


class InterviewTurn(BaseModel):
    question: InterviewQuestion
    answer: str
    evaluation: dict


class InterviewState(BaseModel):
    current_question: InterviewQuestion | None = None
    transcript: list[InterviewTurn] = Field(default_factory=list)
    question_count: int = 0
    min_questions: int = 3
    max_questions: int = 5
    completed: bool = False
    summary: dict | None = None


class InterviewAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=2000)

    @field_validator("answer")
    @classmethod
    def strip_answer(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Interview answer cannot be empty")
        return normalized


class InterviewAnswerResponse(BaseModel):
    job_id: str
    status: str
    interview: InterviewState


class JobStateResponse(BaseModel):
    job_id: str
    status: str
    steps: list[StepUpdate]
    interview: InterviewState | None = None
    report_url: str | None = None
    result: dict | None = None
    error: str | None = None
