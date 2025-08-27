import math
from pathlib import Path

from src.config import PageConfig, Size, Content
from src.svg_generator import TableGenerator, PageGenerator, SvgConfig


def make_bookmark_svgs(data: Content, tables: list[TableGenerator], config: PageConfig) -> list[str]:
    conf = SvgConfig(
        page_config=config,
        title_offset=30,
        table_x_offset=20,
        table_y_offset=70,
        footer_margin=12,
        qr_size=35,
    )
    return [PageGenerator(conf, data.title, data.subtitle, data.url, data.logo, table).build() for table in tables]


def write_svgs(data: Content, bookmarks: list[TableGenerator], config: PageConfig, out_dir_str: str) -> None:
    pages = make_bookmark_svgs(data, bookmarks, config)
    out_dir = Path(out_dir_str)
    out_dir.mkdir(exist_ok=True)

    for i, page in enumerate(pages, 1):
        with Path(out_dir / f"bookmark{i}.svg").open("w", encoding="utf8") as file:
            file.write(page)

def custom_round(num: float) -> int:
    if abs(num - int(num)) >= 0.95:
        return math.ceil(num)
    return math.floor(num)

def make_printable_html(bookmarks: list[str], conf: PageConfig) -> str:
    orientation = "Landscape"
    A4 = Size(width=29.7, height=21)
    if conf.size_cm.height >= A4.height:
        orientation = "Portrait"
        A4 = Size(width=21, height=29.7)

    repeat_in_row = custom_round(A4.width / conf.size_cm.width)
    repeat_in_col = custom_round(A4.height / conf.size_cm.height)
    total_in_page = repeat_in_row * repeat_in_col

    pages = [
        bookmarks[i : i + total_in_page]
        for i in range(0, len(bookmarks), total_in_page)
    ]
    pages_html = '\n<div class="page-break"></div>\n'.join(
        [
            "\n".join(
                [
                    '<div class="svg-container">{}</div>'.format(
                        "\n".join(page[i : i + repeat_in_row])
                    )
                    for i in range(0, total_in_page, repeat_in_row)
                ]
            )
            for page in pages
        ]
    )

    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8" />
            <meta name="pdfkit-page-size" content="A4"/>
            <meta name="pdfkit-orientation" content="{orientation}"/>
            <meta name="pdfkit-margin-top" content="2mm"/>
            <meta name="pdfkit-margin-bottom" content="0"/>
            <meta name="pdfkit-margin-right" content="0"/>
            <meta name="pdfkit-margin-left" content="0"/>
            <style>
                @page {{
                    size: A4 {orientation.lower()};
                }}
                .svg-container {{
                    display: grid;
                    grid-template-columns: repeat({repeat_in_row}, 1fr);
                    grid-gap: 5px;
                    height: {A4.height}cm; /* A4 {orientation.lower()} width */
                    width: {A4.width}cm; /* A4 {orientation.lower()} height */
                }}

                svg {{
                    width: {conf.size_cm.width}cm;
                    height: {conf.size_cm.height}cm;
                    border: 1px solid #ccc;
                }}

                .page-break {{
                    break-before: page;
                    page-break-before: always;
                }}
            </style>
        </head>
        <body>
            {pages_html}
        </body>
        </html>
    """


def write_html(data: Content, bookmarks: list[TableGenerator], config: PageConfig, out_dir_str: str) -> None:
    html = make_printable_html(make_bookmark_svgs(data, bookmarks, config), config)
    out_dir = Path(out_dir_str)
    out_dir.mkdir(exist_ok=True)

    with Path(out_dir / "bookmarks.html").open("w", encoding="utf8") as file:
        file.write(html)
