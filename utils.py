from pathlib import Path
from typing import List
from config import Cell, Config


def more_col_avaible(left_space: int, conf: Config) -> bool:
    return left_space - conf.total_w_col >= conf.left_margin


def get_idx(conf: Config, csv_lines: int) -> List[Cell]:
    idx = []
    width = conf.size.width - conf.right_page_margin
    cols_for_row = csv_lines / conf.max_lines
    i = 0
    while more_col_avaible(width, conf) and i < cols_for_row:
        idx.append(Cell(width, width - conf.date_width))
        width -= conf.total_w_col
        i += 1
    return idx


def read_csv(filename: str) -> List[Cell]:
    entries = []
    with Path(filename).open("r", encoding="utf8") as file:
        for line in file:
            entries.append(Cell(*line.split(",")[:2]))
    return entries
