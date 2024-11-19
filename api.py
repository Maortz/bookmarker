import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from config import Args
from core import run_from_str
from output_generators import write_html, write_svgs

app = FastAPI(
    title="Daily Bookmark Generator",
    description="Generate bookmark files for daily learning.",
)


@app.post("/bookmarker/html")
async def generate_bookmark(
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
            printer=write_html,
        )
        run_from_str(args)
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
