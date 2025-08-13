from fastapi import FastAPI
from src.book_sched import schedule_by_section
from src.data import fetch
from src.model import ScheduleRequest, ScheduleResponse

app = FastAPI(title="Learning Scheduler")


@app.get("/")
async def root():
    return {"message": "Mishna Learning Schedule API", "version": "1.0"}


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}


@app.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(book_name: str, request: ScheduleRequest):
    """Create a learning schedule based on frequency or total days"""
    books = await fetch(book_name)

    if request.is_section():
        info = schedule_by_section(books, request.section_freq)
        return ScheduleResponse(
            info=info,
            book=book_name,
            total_units=sum(i.total_units for i in info),
            days_to_complete=sum(i.days_to_complete for i in info),
            units_per_day=list(request.section_freq.model_dump(exclude_unset=True).values())[0],
        )
    elif request.is_page():
        pass
    elif request.is_days():
        pass
    return list()
