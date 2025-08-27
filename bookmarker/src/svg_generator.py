from dataclasses import dataclass, field
from io import BytesIO
import qrcode
import qrcode.image.svg as svg
from src.config import Row, PageConfig

@dataclass
class SvgConfig:
    page_config: PageConfig
    middle_width: int = field(init=False)

    title_offset: int
    table_x_offset: int
    table_y_offset: int
    footer_margin: int
    qr_size: int

    def __post_init__(self):
        object.__setattr__(self, "middle_width", self.page_config.size.width // 2)

class TableGenerator:
    def __init__(self, config: PageConfig, idx: list[Row]) -> None:
        self.conf = config
        self.idx = idx
        self.data = list()

    def add_row(self, cell: Row, row_idx: int, column_idx: int) -> None:
        date_w = self.idx[column_idx].date
        info_w = self.idx[column_idx].info

        s1 = f'<text x="{date_w}" y="{row_idx * 10}" text-anchor="end" font-family="Arial" font-size="10" fill="#1A1A1A">{cell.date}</text>'
        if cell.bold:
            s2 = f'<text x="{info_w}" y="{row_idx * 10}" text-anchor="end" font-family="Arial" font-size="10" font-weight="bold" fill="#1A1A1A">{cell.info}</text>'
        else:
            s2 = f'<text x="{info_w}" y="{row_idx * 10}" text-anchor="end" font-family="Arial" font-size="10" fill="#1A1A1A">{cell.info}</text>'

        self.data.append(s1)
        self.data.append(s2)
        if cell.underline:
            sep = f'<line x1="{date_w-100}" y1="{row_idx * 10 + 2}" x2="{date_w}" y2="{row_idx * 10 + 2}" stroke="#88A0B8" stroke-width="0.5"/>'
            self.data.append(sep)


    def build(self) -> str:
        line_margin = 5
        end_of_page = self.conf.size.width - 60
        content_margin = 20
        data = "\n".join(self.data)
        return f"""
        <!-- Table Headers -->
        {_gen_header(self.idx)}
        <line x1="0" y1="{line_margin}" x2="{end_of_page}" y2="{line_margin}" stroke="#88A0B8" stroke-width="1"/>

        <g transform="translate(0, {content_margin})">
            {data}
        </g>
        """

class PageGenerator:
    def __init__(self, conf: SvgConfig, title: str, subtitle: str, url: str, logo: str, table: TableGenerator) -> None:
        self.conf = conf
        self.title = title
        self.subtitle = subtitle
        self.url = url
        self.logo = logo
        self.table = table

    def get_page(self, frame_margin: int = 10) -> str:
        return f"""
        <!-- Background -->
        <rect width="{self.conf.page_config.size.width}" height="{self.conf.page_config.size.height}" fill="#B0C4DE"/>
        <rect x="{frame_margin}" y="{frame_margin}" width="{self.conf.page_config.size.width - 2*frame_margin}" height="{self.conf.page_config.size.height - 2*frame_margin}" fill="#fff" stroke="#88A0B8" stroke-width="2"/>
        """
    
    def get_title(self, title: str, subtitle: str) -> str:
        subtitle_margin = 15
        return f"""
        <!-- Title Section -->
        <g transform="translate({self.conf.middle_width}, {self.conf.title_offset})">
            <text x="0" y="0" text-anchor="middle" font-family="Arial" font-size="18" fill="#2C3E50">{title}</text>
            <text x="0" y="{subtitle_margin}" text-anchor="middle" font-family="Arial" font-size="10" fill="#2C3E50">{subtitle}</text>
        </g>
        """
    
    def get_table(self) -> str:
        return f"""
        <g transform="translate({self.conf.table_x_offset}, {self.conf.table_y_offset})">
            {self.table.build()}
        </g>
        """
    
    def get_footer(self, url: str, logo: str) -> str:
        y_offset = self.conf.page_config.size.height - 2 * self.conf.footer_margin - self.conf.qr_size - 2
        qr_margin = 5
        space = 2
        return f"""
        <!-- Fotter -->
        <g transform="translate({self.conf.middle_width},{y_offset})">
            <g transform="translate({0 - self.conf.qr_size - space},0)">
                {_qr_svg_snippet(url)}
            </g>
            <image href="{logo}" x="{space}" y="{qr_margin}" height="{self.conf.qr_size - 2 * qr_margin}" />
            <text x="0" y="{self.conf.qr_size + space}" text-anchor="middle" font-family="Arial" font-size="8">{url}</text>
        </g>
        """
    
    def build(self) -> str:
        frame_margin = 10

        return f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{self.conf.page_config.size_cm.width}cm" height="{self.conf.page_config.size_cm.height}cm" viewBox="0 0 {self.conf.page_config.size.width} {self.conf.page_config.size.height}">
        {self.get_page(frame_margin)}
        <g transform="translate(0,{frame_margin})">
            {self.get_title(self.title, self.subtitle)}
            {self.get_table()}
            {self.get_footer(self.url, self.logo)}
        </g>
        </svg>
        """

def col_to_svg(col: Row, row: int, page: int, idx: list[Row]) -> str:
    date_w = idx[page].date
    info_w = idx[page].info

    s1 = f'<text x="{date_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10" fill="#1A1A1A">{col.date}</text>'
    if col.bold:
        s2 = f'<text x="{info_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10" font-weight="bold" fill="#1A1A1A">{col.info}</text>'
    else:
        s2 = f'<text x="{info_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10" fill="#1A1A1A">{col.info}</text>'

    if not col.underline:
        return f"{s1}\n{s2}"
    return f'{s1}\n{s2}\n<line x1="{date_w-100}" y1="{row * 10 + 2}" x2="{date_w}" y2="{row * 10 + 2}" stroke="#88A0B8" stroke-width="0.5"/>'


def get_svg_tables(column: list[Row], conf: PageConfig, idx: list[Row]) -> list[TableGenerator]:
    out_files = [TableGenerator(conf, idx)]
    column_counter = 0
    visited_rows = 0

    for i, cell in enumerate(column):
        row = i - visited_rows
        if row >= conf.max_lines:
            visited_rows = i
            row = 0
            column_counter += 1

            if column_counter >= len(idx):
                column_counter = 0
                out_files.append(TableGenerator(conf, idx))

        out_files[-1].add_row(cell, row, column_counter)

    return out_files


def _gen_header(idx: list[Row]) -> str:
    s = []
    for date, info, _, _ in idx:
        s.append(
            f'<text x="{date}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#2C3E50">תאריך</text>'
        )
        s.append(
            f'<text x="{info - 10}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#2C3E50">קריאה</text>'
        )
    return "\n".join(s)

def _qr_svg_snippet(url: str) -> str:
    """Generate QR code SVG snippet (only the <svg> content) as string."""
    img = qrcode.make(url, image_factory=svg.SvgPathImage)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    buf.readline() # skip first xml line
    qr_svg = buf.read().decode("utf-8")
    
    # Remove outer <svg> tags to just get inner content
    inner = qr_svg.strip()
    if inner.startswith("<svg"):
        inner = inner[inner.find(">")+1:]
    if inner.endswith("</svg>"):
        inner = inner[:inner.rfind("</svg>")]
    
    return inner
