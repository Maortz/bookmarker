from pydantic import BaseModel, model_validator


# Inner Models

Section = str
Chapter = list[Section]
Book = list[Chapter]
Corpus = list[Book]


class BookData(BaseModel):
    bookname: str
    book: Book


# Input Models


class SectionInterval(BaseModel):
    section: int
    chapter: int

    @model_validator(mode="after")
    def _mutual_exclusivity_validator(self):
        non_empty = [k for k, v in self.model_dump().items() if v]

        if len(non_empty) > 1:
            raise ValueError(f"Cannot have multiple options: {non_empty}")
        return self


class ScheduleRequest(BaseModel):
    section_freq: SectionInterval
    page_freq: int
    total_days: int

    def is_section(self) -> bool:
        return any(self.section_freq.model_dump().values())

    def is_page(self) -> bool:
        return bool(self.page_freq)

    def is_days(self) -> bool:
        return bool(self.total_days)

    @model_validator(mode="after")
    def _mutual_exclusivity_validator(self):
        is_section = int(self.is_section())
        non_empty = [k for k, v in self.model_dump().items() if v]
        c = len(non_empty) - 1 + is_section

        if c > 1:
            raise ValueError(f"Cannot have multiple options: {non_empty}")
        if c == 0:
            raise ValueError("Must choose one option")
        return self


# Output Models


class Bookmark(BaseModel):
    """1-indexed representation"""

    pass


class SectionsBookmark(Bookmark):
    section: int | None = None
    chapter: int | None = None
    part: int | None = None

    @model_validator(mode="after")
    def not_empty_validator(self):
        if not any(self.model_dump().values()):
            raise ValueError("One field should be non-empty")
        return self


class PageBookmark(Bookmark):
    page: int


class ScheduleResponse(BaseModel):
    schedule: list[SectionsBookmark]
    book: str
    total_units: int
    days_to_complete: int
    units_per_day: int
