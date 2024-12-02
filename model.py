from typing import Optional
from pydantic import BaseModel, model_validator


Section = str
Chapter = list[Section]
Book = list[Chapter]
Corpus = list[Book]


class ScheduleRequest(BaseModel):
    section_freq: Optional[int] = None
    chapter_freq: Optional[int] = None
    page_freq: Optional[int] = None
    total_days: Optional[int] = None

    @model_validator(mode="after")
    def _mutual_exclusivity_validator(self):
        non_empty = [k for k, v in self.model_dump().items() if v]
        if len(non_empty) > 1:
            raise ValueError(f"Cannot have multiple options: {non_empty}")
        return self


class SectionInterval(BaseModel):
    section: Optional[int] = None
    chapter: Optional[int] = None
    part: Optional[int] = None

    @model_validator(mode="after")
    def not_empty_validator(self):
        if not any(self.model_dump().values()):
            raise ValueError("One field should be non-empty")
        return self


class Bookmark(BaseModel):
    """1-indexed representation"""

    pass


class SectionsBookmark(Bookmark):
    section: Optional[int] = None
    chapter: Optional[int] = None
    part: Optional[int] = None

    @model_validator(mode="after")
    def not_empty_validator(self):
        if not any(self.model_dump().values()):
            raise ValueError("One field should be non-empty")
        return self


class PageBookmark(Bookmark):
    page: int


class ScheduleResponse(BaseModel):
    schedule: list[SectionsBookmark]
    total_units: int
    days_to_complete: int
    units_per_day: int
