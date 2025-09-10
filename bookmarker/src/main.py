import base64
import datetime
import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import Args, Content, Logo
from src.core import from_str, create_bookmark
from src.input_generator import HebrewCalendar
from src.output_generators import write_html, write_svgs
from src.utils import convert_date, get_simhat_tora_by

app = FastAPI(
    title="Daily Bookmark Generator",
    description="Generate bookmark files for daily learning.",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}


@app.get("/bookmarker/tanah_yomi")
async def gen_tanah_htmlpage(
    year: str = Query(
        ...,
        description="Hebrew year (in the format of התשפה, or just תשפה with default 5000)",
        examples=["התשפה", "תשפה"],
    ),
    width: float = Query(10, description="Bookmark width (cm)"),
    height: float = Query(15, description="Bookmark height (cm)"),
    font: float = Query(12, description="Font size"),
):
    try:
        simhas_torah_dates = get_simhat_tora_by(year)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=exc.args[0])
    
    calendar = HebrewCalendar(
        *simhas_torah_dates,
        major_holidays=True,
        minor_holidays=False,
        extra_holidays=True,
    )

    days = calendar.learning_days(shabbos=True)
    if days < 293:
        raise HTTPException(
            status_code=404, detail="Tanah Yomi Seder doesn't fits calender days"
        )
    if days > 297:
        days = 297

    csv_decoded = Path(f"examples/tanah_yomi_{days}.csv").read_text(encoding="utf-8")
    chapters_lines = csv_decoded.splitlines()
    full_bookmark = calendar.generate_csv(
        iter(chapters_lines),
        shabbos=True,
        bold=True,
    )

    y = simhas_torah_dates[0].hebrew_year(True, True)
    logo = base64.b64encode(Path("images/TanachLogo.png").read_bytes()).decode("utf-8")

    with tempfile.TemporaryDirectory() as tmpdirname:
        title = f'לוח תנ"ך יומי - {y}'
        args = Args(
            input=full_bookmark,
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_html,
        )
        content = Content(
            title=title, 
            subtitle='לימוד כל התנ"ך בשנה אחת - עפ"י חלוקת המסורה',
            url="www.tanachyomi.co.il",
            logo=Logo(content_type="image/png", base64_data=logo),
        )
        create_bookmark(args, content)
        html = (Path(tmpdirname) / "bookmarks.html").read_text(encoding="utf-8")
        return HTMLResponse(html)


@app.post("/bookmarker/html")
async def generate_html(
    start_date: datetime.date = Query(
        ...,
        description="Start date (in the format of 2024-10-03)",
        examples=["2024-10-03"],
    ),
    end_date: datetime.date | None = Query(
        None,
        description="End date, inclusive (default to 1 hebrew year)",
        examples=[None, "2025-09-22"],
    ),
    csv_file: UploadFile = File(..., description="CSV file with chapters (single column)"),
    title: str = Query("Title", description="Title"),
    subtitle: str | None = Query(None, description="Sub Title"),
    logo: UploadFile | None = None,
    url: str|None = Query(None, description="Link on the bookmark"),
    width: float = Query(10, description="Bookmark width (cm)"),
    height: float = Query(15, description="Bookmark height (cm)"),
    font: float = Query(12, description="Font size"),
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
    csv_content = await csv_file.read()
    csv_decoded = csv_content.decode("utf-8")
    chapters_lines = csv_decoded.splitlines()
    bookmark_csv = HebrewCalendar(
        *convert_date(start_date, end_date),
        major_holidays=major_holidays,
        minor_holidays=minor_holidays,
        extra_holidays=extra_holidays,
    ).generate_csv(
        iter(chapters_lines),
        shabbos=shabbos,
        bold=bold,
    )

    encoded_logo = None
    if logo:
        content = await logo.read()
        encoded_logo = Logo(logo.content_type, base64.b64encode(content).decode("utf-8"))
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        args = Args(
            input=bookmark_csv,
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_html,
        )
        content = Content(
            title=title, 
            subtitle=subtitle,
            url=url,
            logo=encoded_logo,
        )
        create_bookmark(args ,content)
        return StreamingResponse(
            StringIO((Path(tmpdirname) / "bookmarks.html").read_text(encoding="utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=bookmarks.html"},
        )


@app.post("/bookmarker/svgs")
async def generate_svgs(
    csv_file: UploadFile = File(..., description="CSV file with date and chapter (2 columns)"),
    title: str = Query("Title", description="Title"),
    subtitle: str|None = Query(None, description="Sub Title"),
    width: float = Query(10, description="Bookmark width (cm)"),
    height: float = Query(15, description="Bookmark height (cm)"),
    font: float = Query(12, description="Font size"),
    logo: UploadFile | None = None,
    url: str|None = Query(None, description="Link on the bookmark"),
):
    csv_content = await csv_file.read()
    csv_decoded = csv_content.decode("utf-8")

    encoded_logo = None
    if logo:
        content = await logo.read()
        encoded_logo = Logo(logo.content_type, base64.b64encode(content).decode("utf-8"))
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        args = Args(
            input=from_str(csv_decoded),
            out=tmpdirname,
            width=width,
            height=height,
            font_size=font,
            printer=write_svgs,
        )
        content = Content(
            title=title, 
            subtitle=subtitle,
            url=url,
            logo=encoded_logo,
        )
        create_bookmark(args, content)
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
