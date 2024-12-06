from pathlib import Path

from src.config import Row, Config, Size
from src.svg_generator import generate_svg


def make_bookmark_svgs(
    pages: list[list[str]], config: Config, idx: list[Row]
) -> list[str]:
    return [generate_svg("\n".join(page), config, idx) for page in pages]


def write_svgs(
    bookmarks: list[list[str]], config: Config, idx: list[Row], out_dir: str
) -> None:
    pages = make_bookmark_svgs(bookmarks, config, idx)
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    for i, page in enumerate(pages, 1):
        with Path(out_dir / f"bookmark{i}.svg").open("w", encoding="utf8") as file:
            file.write(page)


def make_printable_html(bookmarks: list[str], conf: Config) -> str:
    orientation = "Landscape"
    A4 = Config.fix_a4(Size(width=30, height=21))
    if conf.size_cm.height > A4.height:
        orientation = "Portrait"
        A4 = Config.fix_a4(Size(width=21, height=30))

    repeat_in_row = int(A4.width // conf.size_cm.width)
    repeat_in_col = int(A4.height // conf.size_cm.height)
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
                .svg-container {{
                    display: grid;
                    grid-template-columns: repeat({repeat_in_row}, 1fr);
                    grid-gap: 5px;
                    width: 29.7cm; /* A4 landscape width */
                    height: 21cm; /* A4 landscape height */
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


def write_html(
    bookmarks: list[list[str]], config: Config, idx: list[Row], out_dir: str
) -> None:
    html = make_printable_html(make_bookmark_svgs(bookmarks, config, idx), config)
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    with Path(out_dir / "bookmarks.html").open("w", encoding="utf8") as file:
        file.write(html)
