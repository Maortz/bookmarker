from collections import namedtuple
from dataclasses import dataclass, field
from typing import Callable, Any

Size = namedtuple("Size", ["width", "height"])
Row = namedtuple("Row", ["date", "info", "bold", "underline"], defaults=(None,)*4)

@dataclass(frozen=False)
class PageConfig:
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
        object.__setattr__(self, "size_cm", self.limit_to_A4())
        size = self.cm_to_points(self.size_cm)
        object.__setattr__(self, "size", size)
        object.__setattr__(self, "total_w_col", self.date_width + self.info_witdh)
        object.__setattr__(self, "max_lines", (size.height - self.height_margins) // 10)

    def limit_to_A4(self) -> Size:
        h = self.size_cm.height if self.size_cm.height < 29.7 else 29.7
        w = self.size_cm.width if self.size_cm.width < 29.7 else 29.7
        return Size(height=h, width=w)        

    def cm_to_points(self, s_cm: Size) -> Size:
        convert_ratio = 10 * self.ratio
        return Size(s_cm.width * convert_ratio, s_cm.height * convert_ratio)

Logo = namedtuple("Logo", ["content_type", "base64_data"])

@dataclass
class Content:
    title: str
    subtitle: str|None
    url: str|None
    logo: Logo|None

@dataclass
class Args:
    input: list[Row]
    out: str
    width: float
    height: float
    font_size: int
    printer: Callable[[Content, list[Any], PageConfig, str], None]
