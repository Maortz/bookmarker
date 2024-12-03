import math
import operator
from itertools import accumulate

from fastapi import FastAPI, HTTPException

from data import fetch
from model import Book, ScheduleRequest, ScheduleResponse, SectionsBookmark

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
    yield SectionsBookmark(chapter=len(book), section=accumulated_sections[-1] - accumulated_sections[last_chapter - 1])


def create_daily_schedule(
    chapters: Book,
    section_freq: int = None,
    total_days: int = None,
    book_name: str = None
):
    if section_freq and total_days:
        raise HTTPException(
            status_code=400, detail="Specify either frequency or total_days, not both"
        )

    total_sections = sum(len(ch) for ch in chapters)

    if section_freq:
        days_to_complete = math.ceil(total_sections / section_freq)
        section_per_day = section_freq
    elif total_days:
        section_per_day = math.ceil(total_sections / total_days)
        days_to_complete = total_days
    else:
        # Default 2 chapters a day if neither is specified
        section_per_day = 2
        days_to_complete = math.ceil(total_sections / section_per_day)

    chapters = get_book_bookmarks(chapters, section_per_day)

    return ScheduleResponse(
        schedule=list(chapters),
        total_units=total_sections,
        days_to_complete=days_to_complete,
        units_per_day=section_per_day,
        book=book_name
    )


@app.get("/")
async def root():
    return {"message": "Mishna Learning Schedule API", "version": "1.0"}


@app.post("/schedule", response_model=list[ScheduleResponse])
async def create_schedule(book: str, request: ScheduleRequest):
    """Create a learning schedule based on frequency or total days"""
    books = await fetch(book)
    responses = [
        create_daily_schedule(
            chapters[1],
            section_freq=request.section_freq,
            total_days=request.total_days,
            book_name=chapters[0]
        )
        for chapters in books
    ]
    return responses
