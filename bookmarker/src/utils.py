from pathlib import Path
from typing import Iterable

from src.config import Row, Config


def more_col_avaible(left_space: int, conf: Config) -> bool:
    return left_space - conf.total_w_col >= conf.left_margin


def get_idx(conf: Config, csv_lines: int) -> list[Row]:
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
        entries.append(Row(*line.split(",")[:len(Row._fields)]))
    return entries
