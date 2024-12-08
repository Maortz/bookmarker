import asyncio
from aiocache import cached
import json
import traceback
import urllib
from pathlib import Path

import httpx
from fastapi import HTTPException

from src.model import Book, BookData

@cached()
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


def find_category_in_index(book: str, idx_json: dict) -> dict | None:
    alt = book.split(" ")[0]
    for d in idx_json:
        if d["category"] in {book, alt}:
            if (alt2 := book.split(" ")[-1]) != alt:
                for d2 in d["contents"]:
                    if d2["category"] in {book, alt, alt2}:
                        return d2["contents"]
            return d["contents"]
    return None


def find_corpus_in_category(book: str, category: dict) -> list[str]:
    if not book:
        return list()
    alt = book.split(" ")[-1]
    try:
        return [
            d2["title"]
            for d1 in category
            for d2 in d1["contents"]
            if d2.get("corpus", "XXX") in {book, alt}
        ]
    except KeyError as ke:
        print(traceback.print_exception(ke))
        return list()


def find_corpus(book: str):
    with Path("../resource/index.json").open("r", encoding="utf-8-sig") as fd:
        idx = json.load(fd)
    cat = find_category_in_index(book, idx)
    if cat:
        return find_corpus_in_category(book, cat)


def test_corpus():
    assert len(find_corpus("Mishnah")) == 63
    assert len(find_corpus("Talmud Bavli")) == 38
    assert len(find_corpus("Talmud Yerushalmi")) == 38

@cached()
async def fetch(book: str):
    # try single book (text)
    try:
        mishna_data = await fetch_data_by_text(book)
        return [BookData(bookname=book, book=parse_text_structure(mishna_data))]
    except HTTPException:
        pass
    # try corpus (text)
    books = find_corpus(book)
    if not books:
        raise HTTPException(status_code=400, detail="Book not found")

    async def process_book(book):
        mishna_data = await fetch_data_by_text(book)
        return BookData(bookname=book, book=parse_text_structure(mishna_data))

    tasks = [process_book(book) for book in books]
    return await asyncio.gather(*tasks)
