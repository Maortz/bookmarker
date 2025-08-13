from pydantic import BaseModel


class SectionInterval(BaseModel):
    section: int | None = None
    chapter: int | None = None

class BookmarkRequest(BaseModel):
    book_name: str
    section_freq: SectionInterval
    page_freq: int | None = None
    total_days: int | None = None