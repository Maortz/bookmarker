import asyncio
import math
import operator
import urllib
import urllib.parse
from itertools import accumulate

import httpx
from fastapi import FastAPI, HTTPException

from model import Book, ScheduleRequest, ScheduleResponse, SectionsBookmark

app = FastAPI(title="Learning Scheduler")


async def fetch_data_by_text(book: str) -> dict:
    """Fetch Mishna Zraim data from Sefaria API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://www.sefaria.org/api/v3/texts/{urllib.parse.quote(book)}"
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=503, detail="Failed to fetch data from Sefaria"
                )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=503, detail="Failed to connect to Sefaria API"
            )


def parse_text_structure(data: dict) -> Book:
    """Extract chapter information from Sefaria data"""
    return data["versions"][0]["text"]


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
    yield SectionsBookmark(chapter=len(book), section=accumulated_sections[-1])


def create_daily_schedule(
    chapters: Book,
    section_freq: int = None,
    total_days: int = None,
):
    if section_freq and total_days:
        raise HTTPException(
            status_code=400, detail="Specify either frequency or total_days, not both"
        )

    total_chapters = len(chapters)
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
        total_units=total_chapters,
        days_to_complete=days_to_complete,
        units_per_day=section_per_day,
    )


@app.get("/")
async def root():
    return {"message": "Mishna Learning Schedule API", "version": "1.0"}


@app.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(book: str, request: ScheduleRequest):
    """Create a learning schedule based on frequency or total days"""
    mishna_data = await fetch_data_by_text(book)
    chapters = parse_text_structure(mishna_data)

    return create_daily_schedule(
        chapters,
        section_freq=request.section_freq,
        total_days=request.total_days,
    )


async def main():
    req = ScheduleRequest(section_freq=2)
    f = await create_schedule("Mishnah Berakhot", req)
    print(f)

if __name__ == "__main__":
    asyncio.run(main())

