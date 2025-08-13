import datetime

from fastapi import FastAPI, Query
from src.model import BookmarkRequest
from src.orchestrator import BookLearningOrchestrator

app = FastAPI(title="Book Learning Orchestrator")


@app.post("/create-book-learning-plan")
async def create_book_learning_plan(
    book_details: BookmarkRequest,
    width: int = Query(10, description="Bookmark width (cm)"),
    height: int = Query(15, description="Bookmark height (cm)"),
    font: int = Query(12, description="Font size"),
    start_date: datetime.date = Query(
        ...,
        description="Start date (in the format of 2024-10-03)",
        examples=["2024-10-03"],
    ),
    shabbat: bool = Query(True, description="Do not schedule learning on Shabbat"),
):
    orchestrator = BookLearningOrchestrator()
    return await orchestrator.create_learning_plan(
        book_details, width, height, font, start_date, shabbat
    )


def start_service():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
