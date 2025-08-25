from collections import namedtuple
from dataclasses import dataclass, field
from typing import Callable

Size = namedtuple("Size", ["width", "height"])
Row = namedtuple("Row", ["date", "info", "bold", "underline"], defaults=(None,)*4)

@dataclass(frozen=True)
class Config:
    size_cm: Size
    ratio: float

    size: Size = field(init=False)
    right_page_margin: int = 60
    height_margins: int = 110 + 40
    date_width: int = 40
    info_witdh: int = 80
    left_margin: int = -20
    total_w_col: int = field(init=False)
    max_lines: int = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "ratio", 48 / self.ratio)
        size = self.cm_to_points(self.size_cm)
        object.__setattr__(self, "size", size)
        object.__setattr__(self, "total_w_col", self.date_width + self.info_witdh)
        object.__setattr__(self, "max_lines", (size.height - self.height_margins) // 10)

    def cm_to_points(self, s_cm: Size) -> Size:
        convert_ratio = 10 * self.ratio
        return Size(s_cm.width * convert_ratio, s_cm.height * convert_ratio)

    @staticmethod
    def fix_a4(s: Size) -> Size:
        a4_fix = 1
        return Size(a4_fix * s.width, a4_fix * s.height)


@dataclass
class Args:
    input: list[Row]
    out: str
    width: int
    height: int
    font_size: int
    title: str
    subtitle: str
    printer: Callable[[str, list[list[str]], Config, list[Row], str], None]
