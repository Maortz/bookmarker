import datetime
from pathlib import Path
from typing import Iterable

from pyluach.dates import HebrewDate
from src.config import PageConfig, Row


def more_col_avaible(left_space: int, conf: PageConfig) -> bool:
    return left_space - conf.total_w_col >= conf.left_margin


def get_idx(conf: PageConfig, csv_lines: int) -> list[Row]:
    idx = []
    width = conf.size.width - conf.right_page_margin
    cols_for_row = csv_lines / conf.max_lines
    i = 0
    while more_col_avaible(width, conf) and i < cols_for_row:
        idx.append(Row(width, width - conf.date_width))
        width -= conf.total_w_col
        i += 1
    return idx


def read_csv(filename: str) -> list[Row]:
    with Path(filename).open("r", encoding="utf8") as file:
        return parse_csv(file)


def parse_csv(csv_content: Iterable[str]) -> list[Row]:
    entries = []
    for line in csv_content:
        entries.append(Row(*line.split(",")[: len(Row._fields)]))
    return entries


def convert_date(
    start_date: datetime.date, end_date: datetime.date | None = None
) -> tuple[HebrewDate, HebrewDate]:
    start_date = HebrewDate.from_pydate(start_date)
    if end_date:
        end_date = HebrewDate.from_pydate(end_date)
    else:
        end_date = start_date.add(years=1).subtract(days=1)
    return start_date, end_date


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
    if ord(ch) in (ord("ם"), ord("ן"), ord("ץ"), ord("ף"), ord("ך")):
        raise Exception(f"Not handling מנצפך letters (got {ch})")
    return ord(ch) - ord("א") + 1


def get_heb_year(year: str) -> int:
    if not isinstance(year, str) or len(year) > 5 or not year:
        raise Exception("Not a valid hebrew year")
    thousands = 1000 * heb_to_int(year[0])
    if thousands > 6000:
        return 5000 + sum(map(heb_to_int, year))
    return thousands + sum(map(heb_to_int, year[1:]))


def get_simhat_tora_by(year: str) -> tuple[HebrewDate, HebrewDate]:
    s = HebrewDate(get_heb_year(year), 7, 23)
    return s, s.add(years=1).subtract(days=1)
