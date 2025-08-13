import csv
import datetime
from io import BytesIO, StringIO

import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from src.model import BookmarkRequest

int_to_heb = {
    1: "א",
    2: "ב",
    3: "ג",
    4: "ד",
    5: "ה",
    6: "ו",
    7: "ז",
    8: "ח",
    9: "ט",
    10: "י",
    20: "כ",
    30: "ל",
    40: "מ",
    50: "נ",
    60: "ס",
    70: "ע",
    80: "פ",
    90: "צ",
    100: "ק",
    200: "ר",
    300: "ש",
    400: "ת",
}


def gimatria(num: int) -> str:
    if isinstance(num, str):
        num = int(num)
    ret = list()
    keys = reversed(int_to_heb.keys())
    try:
        d = next(keys)
        while num > 0:
            if num // d > 0:
                m = num // d
                num -= m * d
                ret.extend([d] * m)
            d = next(keys)
    except StopIteration:
        pass
    return "".join(int_to_heb[x] for x in ret)


class ServiceConfig:
    # SCHEDULER_URL = "https://book-scheduler-service.onrender.com"
    # BOOKMARK_URL = "https://bookmarker-service.onrender.com"
    SCHEDULER_URL = "http://127.0.0.1:8000"
    BOOKMARK_URL = "http://127.0.0.1:8001"


class BookLearningOrchestrator:
    async def get_shcedule(
        self, client: httpx.AsyncClient, book_details: BookmarkRequest
    ) -> list:
        book_name = book_details.book_name
        details = book_details.model_dump(exclude="book_name", exclude_none=True)
        url = f"{ServiceConfig.SCHEDULER_URL}/schedule?book_name={book_name}"

        schedule_response = await client.post(url, json=details, timeout=None)
        return [
            (d["book"], f"{gimatria(sch['chapter'])} {gimatria(sch['section'])}")
            for d in schedule_response.json()["info"]
            for sch in d["schedule"]
        ]

    def short_booknames(self, schedule_lst: list) -> list:
        booknames = [x[0].split(" ") for x in schedule_lst]
        i = 0
        try:
            while all(x[i] == booknames[0][i] for x in booknames):
                i += 1
        except IndexError:
            pass
        j = -1
        try:
            while all(x[j] == booknames[0][j] for x in booknames):
                j -= 1
        except IndexError:
            pass
        j += 1
        if j == 0:
            j = None

        return [
            f'{" ".join(bookname[i:j])} {schd[1]}'
            for bookname, schd in zip(booknames, schedule_lst)
        ]

    def make_csv_file_stream(self, lst: list) -> tuple:
        output = StringIO()
        writer = csv.writer(output)
        for item in lst:
            writer.writerow([item])
        return ("data.csv", output.getvalue(), "text/csv")

    async def create_learning_plan(
        self,
        book_details: BookmarkRequest,
        width: int,
        height: int,
        font: int,
        start_date: datetime.date,
        shabbat: bool,
    ):
        async with httpx.AsyncClient() as client:
            try:
                schedule_lst = await self.get_shcedule(client, book_details)
                csv_list = self.short_booknames(schedule_lst)
                files = self.make_csv_file_stream(csv_list)
                bookmark_response = await client.post(
                    f"{ServiceConfig.BOOKMARK_URL}/bookmarker/html?width={width}&height={height}&font={font}&start_date={start_date}&shabbos={shabbat}&major_holidays=true&minor_holidays=false&extra_holidays=true&bold=true",
                    files={"csv_file": files},
                )
                bookmarks_data = bookmark_response.content
                return StreamingResponse(
                    BytesIO(bookmarks_data),
                    media_type="text/html",
                    headers={
                        "Content-Disposition": "attachment; filename=bookmarks.html"
                    },
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503, detail=f"Service unavailable: {str(exc)}"
                )
