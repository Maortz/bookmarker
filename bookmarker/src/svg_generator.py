from io import BytesIO
import qrcode
import qrcode.image.svg as svg
from src.config import Row, Config

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


def get_svg_lines(column: list[Row], conf: Config, idx: list[Row]) -> list[list[str]]:
    out_files = [[]]
    page_counter = 0
    visited_rows = 0

    for i, cell in enumerate(column):
        row = i - visited_rows
        if row >= conf.max_lines:
            visited_rows = i
            row = 0
            page_counter += 1

            if page_counter >= len(idx):
                page_counter = 0
                out_files.append([])

        out_files[-1].append(col_to_svg(col=cell, row=row, page=page_counter, idx=idx))

    return out_files


def gen_header(idx: list[Row]) -> str:
    s = []
    for date, info, _, _ in idx:
        s.append(
            f'<text x="{date}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#2C3E50">תאריך</text>'
        )
        s.append(
            f'<text x="{info - 10}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#2C3E50">קריאה</text>'
        )
    return "\n".join(s)

def qr_svg_snippet(url: str) -> str:
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

# def _approx_text_width(text: str, font_size: int = 10, avg_em: float = 0.46) -> int:
#     """
#     Very light heuristic for text width in px.
#     avg_em≈0.56 works decently for Arial 8–14px. Adjust if needed.
#     """
#     return max(1, int(round(len(text) * font_size * avg_em)))

def generate_svg(title: str, data: str, conf: Config, idx: list[Row], url="www.tanachyomi.co.il") -> str:
    frame_margin = 10
    title_offset = 30 + frame_margin
    headers_y_offset = 40 + title_offset
    headers_x_offset = 20 + frame_margin
    data_y_offset = headers_y_offset + 20
    data_x_offset = headers_x_offset
    footer_margin = 8
    qr_size = 35

    subtitle = 'לימוד כל התנ"ך בשנה אחת - עפ"י חלוקת המסורה'
    footer_y_offset = conf.size.height - 2 * footer_margin - qr_size - 2
    footer_x_offset = conf.size.width // 2 - qr_size - 5


    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"  width="{conf.size_cm.width}cm" height="{conf.size_cm.height}cm" viewBox="0 0 {conf.size.width} {conf.size.height}">
    <!-- Background -->
    <rect width="{conf.size.width}" height="{conf.size.height}" fill="#B0C4DE"/>
    <rect x="{frame_margin}" y="{frame_margin}" width="{conf.size.width - 2*frame_margin}" height="{conf.size.height - 2*frame_margin}" fill="#fff" stroke="#88A0B8" stroke-width="2"/>
    
    <!-- Title Section -->
    <g transform="translate({conf.size.width // 2}, {title_offset})">
        <text x="0" y="0" text-anchor="middle" font-family="Arial" font-size="18" fill="#2C3E50">{title}</text>
        <text x="0" y="15" text-anchor="middle" font-family="Arial" font-size="10" fill="#2C3E50">{subtitle}</text>
    </g>

    <!-- Headers -->
    <g transform="translate({headers_x_offset}, {headers_y_offset})">
        {gen_header(idx)}
        <line x1="0" y1="5" x2="{conf.size.width - 60}" y2="5" stroke="#88A0B8" stroke-width="1"/>
    </g>

    <g transform="translate({data_x_offset}, {data_y_offset})">
    {data}
    </g>

    <!-- Fotter -->
    <g transform="translate({footer_x_offset},{footer_y_offset})">
        {qr_svg_snippet(url)}
        <text x="{qr_size + 5}" y="{qr_size + 2}" text-anchor="middle" font-family="Arial" font-size="8">{url}</text>
        <image href="images/TanachLogo.png" x="{qr_size + 2}" y="{5}" height="{qr_size - 10}" />
    </g>
    
    <!-- Corner Ornaments -->
    <g fill="none" stroke="#88A0B8" stroke-width="1">
        <path d="M20 20 C 20 30, 30 30, 30 20"/>
        <path d="M{conf.size.width - 30} 20 C {conf.size.width - 30} 30, {conf.size.width - 40} 30, {conf.size.width - 40} 20"/>
        <path d="M20 {conf.size.height - 30} C 20 {conf.size.height - 40}, 30 {conf.size.height - 40}, 30 {conf.size.height - 30}"/>
        <path d="M{conf.size.width - 30} {conf.size.height - 30} C {conf.size.width - 30} {conf.size.height - 40}, {conf.size.width - 40} {conf.size.height - 40}, {conf.size.width - 40} {conf.size.height - 30}"/>
    </g>
    </svg>
    """
