from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class InvalidAllocationRequestError(Exception):
    """Raised when an allocation request or its components are invalid."""
    pass


class MemberData(BaseModel):
    """Represents a household member available for chore assignment."""
    id: int
    name: str


class ChoreData(BaseModel):
    """Represents a chore that needs to be assigned."""
    id: int
    title: str
    effort_level: int = Field(..., description="Estimated effort level between 1 (Low) and 3 (High)")
    frequency: str

    @field_validator("effort_level")
    @classmethod
    def validate_effort_level(cls, v: int) -> int:
        if not (1 <= v <= 3):
            raise InvalidAllocationRequestError(f"effort_level must be an integer between 1 and 3, got {v}")
        return v


class WorkloadHistory(BaseModel):
    """Represents recent effort points accumulated by a household member."""
    member_id: int
    recent_effort_sum: int = 0


class ProposedAssignment(BaseModel):
    """Represents a chore assigned to a member with explanation."""
    chore_id: int
    member_id: int
    reasoning: str


class AllocationRequest(BaseModel):
    """Input payload required to compute a chore allocation schedule."""
    members: List[MemberData]
    chores: List[ChoreData] = Field(default_factory=list)
    workload_history: List[WorkloadHistory] = Field(default_factory=list)
    user_notes: Optional[str] = ""

    @field_validator("user_notes", mode="before")
    @classmethod
    def normalize_user_notes(cls, v: Optional[str]) -> str:
        if v is None:
            return ""
        if isinstance(v, str) and not v.strip():
            return ""
        return v

    @model_validator(mode="after")
    def validate_members_not_empty(self) -> "AllocationRequest":
        if not self.members:
            raise InvalidAllocationRequestError("Cannot allocate chores with zero household members.")
        return self


class AllocationResponse(BaseModel):
    """Result of an allocation run containing proposed assignments and summary reasoning."""
    assignments: List[ProposedAssignment] = Field(default_factory=list)
    raw_reasoning_summary: str = ""
    engine_used: str
