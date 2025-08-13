import math
import operator
from itertools import accumulate
from typing import Any, Generator

from src.model import (
    Book,
    BookData,
    BookSchedule,
    SectionInterval,
    SectionsBookmark,
)


def get_sections_bookmarks_of(book: Book, section_interval: int) -> Generator[SectionsBookmark, Any, None]:
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

    chapters = get_sections_bookmarks_of(chapters, section_per_day)

    return BookSchedule(
        schedule=list(chapters),
        book=book.bookname,
        total_units=total_sections,
        days_to_complete=days_to_complete,
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

    return BookSchedule(
        schedule=bookmarks,
        book=book.bookname,
        total_units=total_chapters,
        days_to_complete=days_to_complete,
    )


def schedule_by_section(books: list[BookData], freq: SectionInterval):
    if freq.section:
        return [schedule_book_by_section(book, freq.section) for book in books]
    return [schedule_book_by_chapter(book, freq.chapter) for book in books]
