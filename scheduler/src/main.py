import math
import operator
from itertools import accumulate

from fastapi import FastAPI

from data import fetch
from model import (
    Book,
    BookData,
    ScheduleRequest,
    ScheduleResponse,
    SectionInterval,
    SectionsBookmark,
)

app = FastAPI(title="Learning Scheduler")


def get_book_bookmarks(book: Book, section_interval: int):
    accumulated_sections = [0] + list(accumulate(map(len, book), operator.add))
    last_chapter = 0
    last_section = section_interval
    while last_section <= accumulated_sections[-1]:
        while last_section > accumulated_sections[last_chapter]:
            last_chapter += 1
        yield SectionsBookmark(
            chapter=last_chapter,
            section=last_section - accumulated_sections[last_chapter - 1],
        )
        last_section += section_interval
    yield SectionsBookmark(
        chapter=len(book),
        section=accumulated_sections[-1] - accumulated_sections[last_chapter - 1],
    )


def schedule_book_by_section(book: BookData, section_freq: int = 0):
    chapters = book.book
    total_sections = sum(len(ch) for ch in chapters)

    if section_freq:
        days_to_complete = math.ceil(total_sections / section_freq)
        section_per_day = section_freq
    else:
        # Default 2 sections a day if neither is specified
        section_per_day = 2
        days_to_complete = math.ceil(total_sections / section_per_day)

    chapters = get_book_bookmarks(chapters, section_per_day)

    return ScheduleResponse(
        schedule=list(chapters),
        total_units=total_sections,
        days_to_complete=days_to_complete,
        units_per_day=section_per_day,
        book=book.bookname,
    )


def schedule_book_by_chapter(book: BookData, chapter_freq: int = 0):
    chapters = book.book
    total_chapters = len(chapters)

    if chapter_freq:
        days_to_complete = math.ceil(total_chapters / chapter_freq)
        chapter_per_day = chapter_freq
    else:
        # Default 1 chapters a day if neither is specified
        chapter_per_day = 1
        days_to_complete = math.ceil(total_chapters / chapter_per_day)

    bookmarks = [
        SectionsBookmark(section=1, chapter=i)
        for i in range(chapter_per_day, total_chapters, chapter_per_day)
    ]
    bookmarks.append(SectionsBookmark(section=1, chapter=total_chapters))

    return ScheduleResponse(
        schedule=bookmarks,
        total_units=total_chapters,
        days_to_complete=days_to_complete,
        units_per_day=chapter_per_day,
        book=book.bookname,
    )


def schedule_by_section(books: list[BookData], freq: SectionInterval):
    if freq.section:
        return [schedule_book_by_section(book, freq.section) for book in books]
    return [schedule_book_by_chapter(book, freq.chapter) for book in books]


@app.get("/")
async def root():
    return {"message": "Mishna Learning Schedule API", "version": "1.0"}


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}


@app.post("/schedule", response_model=list[ScheduleResponse])
async def create_schedule(book_name: str, request: ScheduleRequest):
    """Create a learning schedule based on frequency or total days"""
    books = await fetch(book_name)

    if request.is_section():
        return schedule_by_section(books, request.section_freq)
    elif request.is_page():
        pass
    elif request.is_days():
        pass
    return list()
