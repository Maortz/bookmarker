import datetime
import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

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


@app.get("/bookmarker/tanah")
async def gen_tanah_htmlpage(
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
):
    days = learning_days(
        *convert_date(start_date, end_date),
        shabbos=shabbos,
        major_holidays=major_holidays,
        minor_holidays=minor_holidays,
        extra_holidays=extra_holidays,
    )
    if days > 295 or days < 293:
        raise HTTPException(
            status_code=404, detail="Tanah Yomi Seder doesn't fits calender days"
        )
    csv_decoded = Path(f"examples/tanah_yomi_{days}.csv").read_text(encoding="utf-8")
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
