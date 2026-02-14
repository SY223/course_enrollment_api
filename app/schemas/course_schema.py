from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class CourseBase(BaseModel):
    code: str
    title: str

    @field_validator("code") 
    def validate_course_code(cls, value): 
        pattern = r"^[A-Za-z]{3}\d{3}$"
        if not re.match(pattern, value): 
            raise ValueError("Course code must be 3 letters followed by 3 digits (e.g., CSC101)") 
        return value.upper()

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None