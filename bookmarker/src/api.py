import datetime
import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from pyluach.dates import HebrewDate
from src.config import Args
from src.core import run_from_lst, run_from_str
from src.input_generator import convert_date, generate_csv, learning_days
from src.output_generators import write_html, write_svgs

app = FastAPI(
    title="Daily Bookmark Generator",
    description="Generate bookmark files for daily learning.",
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}


def heb_to_int(ch: str) -> int:
    if ord(ch) >= ord("ק"):
        return (ord(ch) - ord("ק") + 1) * 100
    if ord(ch) == ord("צ"):
        return 90
    if ord(ch) == ord("פ"):
        return 80
    if ord(ch) in range(ord("נ"), ord("ע") + 1):
        return (ord(ch) - ord("כ") - 2) * 10
    if ord(ch) == ord("מ"):
        return 40
    if ord(ch) in (ord("כ"), ord("ל")):
        return (ord(ch) - 11) * 10
    return ord(ch) - ord("א") + 1


def get_heb_year(year: str) -> int:
    if not isinstance(year, str) or len(year) > 5 or not year:
        raise
    thousands = 1000 * heb_to_int(year[0])
    return thousands + sum(map(heb_to_int, year[1:]))


def get_simhat_tora_by(year: str) -> tuple[HebrewDate, HebrewDate]:
    s = HebrewDate(get_heb_year(year), 7, 23)
    return s, s.add(years=1).subtract(days=1)


@app.get("/bookmarker/tanah")
async def gen_tanah_htmlpage(
    width: int = Query(10, description="Bookmark width (cm)"),
    height: int = Query(15, description="Bookmark height (cm)"),
    font: int = Query(12, description="Font size"),
    year: str = Query(
        ...,
        description="Hebrew year (in the format of התשפה)",
        examples=["התשפה"],
    ),
    shabbos: bool = Query(True, description="Do not schedule learning on Shabbos"),
    major_holidays: bool = Query(
        True, description="Do not schedule learning on non-working holidays"
    ),
    minor_holidays: bool = Query(
        False,
        description="Do not schedule learning on working holidays (Hanuka, Hol Hamoed, etc.)",
    ),
    extra_holidays: bool = Query(
        True,
        description="Do not schedule learning on Purim, Tishaa Beav and Yom Haatzmaut",
    ),
    bold: bool = Query(True, description="Bold Shabbos or any non-learning day"),
):
    days = learning_days(
        *get_simhat_tora_by(year),
        shabbos=shabbos,
        major_holidays=major_holidays,
        minor_holidays=minor_holidays,
        extra_holidays=extra_holidays,
    )
    if days < 293:
        raise HTTPException(
            status_code=404, detail="Tanah Yomi Seder doesn't fits calender days"
        )
    if days > 297:
        days = 297
    csv_decoded = Path(f"examples/tanah_yomi_{days}.csv").read_text(encoding="utf-8")
    lines = csv_decoded.splitlines()
    input_lines = generate_csv(
        *get_simhat_tora_by(year),
        iter(lines),
        shabbos=shabbos,
        major_holidays=major_holidays,
        minor_holidays=minor_holidays,
        extra_holidays=extra_holidays,
        bold=bold,
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        args = Args(
            input=input_lines,
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_html,
        )
        run_from_lst(args)
        content = (Path(tmpdirname) / "bookmarks.html").read_text(encoding="utf-8")
        return HTMLResponse(content)


@app.post("/bookmarker/html")
async def generate_html(
    width: int = Query(10, description="Bookmark width (cm)"),
    height: int = Query(15, description="Bookmark height (cm)"),
    font: int = Query(12, description="Font size"),
    start_date: datetime.date = Query(
        ...,
        description="Start date (in the format of 2024-10-03)",
        examples=["2024-10-03"],
    ),
    end_date: Optional[datetime.date] = Query(
        None,
        description="End date, inclusive (default to 1 hebrew year)",
        examples=[None, "2025-09-22"],
    ),
    shabbos: bool = Query(True, description="Do not schedule learning on Shabbos"),
    major_holidays: bool = Query(
        True, description="Do not schedule learning on non-working holidays"
    ),
    minor_holidays: bool = Query(
        False,
        description="Do not schedule learning on working holidays (Hanuka, Hol Hamoed, etc.)",
    ),
    extra_holidays: bool = Query(
        True,
        description="Do not schedule learning on Purim, Tishaa Beav and Yom Haatzmaut",
    ),
    bold: bool = Query(True, description="Bold Shabbos or any non-learning day"),
    csv_file: UploadFile = File(..., description="CSV file with chapters"),
):
    csv_content = await csv_file.read()
    csv_decoded = csv_content.decode("utf-8")
    lines = csv_decoded.splitlines()
    input_lines = generate_csv(
        *convert_date(start_date, end_date),
        iter(lines),
        shabbos=shabbos,
        major_holidays=major_holidays,
        minor_holidays=minor_holidays,
        extra_holidays=extra_holidays,
        bold=bold,
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        args = Args(
            input=input_lines,
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_html,
        )
        run_from_lst(args)
        return StreamingResponse(
            StringIO((Path(tmpdirname) / "bookmarks.html").read_text(encoding="utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=bookmarks.html"},
        )


@app.post("/bookmarker/svgs")
async def generate_svgs(
    width: int = Query(10, description="Bookmark width (cm)"),
    height: int = Query(15, description="Bookmark height (cm)"),
    font: int = Query(12, description="Font size"),
    csv_file: UploadFile = File(..., description="CSV file with date and chapter"),
):
    csv_content = await csv_file.read()
    csv_decoded = csv_content.decode("utf-8")

    with tempfile.TemporaryDirectory() as tmpdirname:
        args = Args(
            input=csv_decoded,
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_svgs,
        )
        run_from_str(args)
        zip_path = Path(tmpdirname) / "bookmarks.zip"
        svg_files = list(Path(tmpdirname).glob("*.svg"))
        if svg_files:
            shutil.make_archive(str(zip_path.with_suffix("")), "zip", tmpdirname)
            return StreamingResponse(
                BytesIO(zip_path.read_bytes()),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=bookmarks.zip"},
            )


def start_service():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
