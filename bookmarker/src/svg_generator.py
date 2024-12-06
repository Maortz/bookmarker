from src.config import Row, Config


def col_to_svg(
    col: Row, row: int, page: int, idx: list[Row], bold: bool = False
) -> str:
    date_w = idx[page].date
    info_w = idx[page].info

    s1 = f'<text x="{date_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10">{col.date}</text>'
    if col.bold:
        s2 = f'<text x="{info_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10" font-weight="bold">{col[1]}</text>'
    else:
        s2 = f'<text x="{info_w}" y="{row * 10}" text-anchor="end" font-family="Arial" font-size="10">{col.info}</text>'

    return f"{s1}\n{s2}"


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

        out_files[-1].append(
            col_to_svg(col=cell, row=row, page=page_counter, idx=idx)
        )

    return out_files


def gen_header(idx: list[Row]) -> str:
    s = []
    for date, info, _ in idx:
        s.append(
            f'<text x="{date}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#8b4513">תאריך</text>'
        )
        s.append(
            f'<text x="{info - 10}" y="0" text-anchor="end" font-family="Arial" font-size="12" fill="#8b4513">קריאה</text>'
        )
    return "\n".join(s)


def generate_svg(data: str, conf: Config, idx: list[Row]) -> str:
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"  width="{conf.size_cm.width}cm" height="{conf.size_cm.height}cm" viewBox="0 0 {conf.size.width} {conf.size.height}">
    <!-- Background -->
    <rect width="{conf.size.width}" height="{conf.size.height}" fill="#f7e9d0"/>
    <rect x="10" y="10" width="{conf.size.width - 20}" height="{conf.size.height - 20}" fill="#fff" stroke="#8b4513" stroke-width="2"/>
    
    <!-- Title Section -->
    <text x="{conf.size.width // 2}" y="40" text-anchor="middle" font-family="Arial" font-size="18" fill="#8b4513">לוח תנ"ך יומי</text>
    
    <!-- Headers -->
    <g transform="translate(30, 70)">
        {gen_header(idx)}
        <line x1="0" y1="10" x2="{conf.size.width - 60}" y2="10" stroke="#8b4513" stroke-width="1"/>
    </g>

    <g transform="translate(30, 100)">
    {data}
    </g>

    <!-- Decorative Elements -->
    <path d="M{conf.size.width // 2} {conf.size.height - 20} L {conf.size.width // 2 - 20} {conf.size.height - 5} L {conf.size.width // 2} {conf.size.height - 10} L {conf.size.width // 2 + 20} {conf.size.height - 5} L {conf.size.width // 2} {conf.size.height - 20}" fill="#8b4513"/>
    
    <!-- Corner Ornaments -->
    <g fill="none" stroke="#8b4513" stroke-width="1">
        <path d="M20 20 C 20 30, 30 30, 30 20"/>
        <path d="M{conf.size.width - 30} 20 C {conf.size.width - 30} 30, {conf.size.width - 40} 30, {conf.size.width - 40} 20"/>
        <path d="M20 {conf.size.height - 30} C 20 {conf.size.height - 40}, 30 {conf.size.height - 40}, 30 {conf.size.height - 30}"/>
        <path d="M{conf.size.width - 30} {conf.size.height - 30} C {conf.size.width - 30} {conf.size.height - 40}, {conf.size.width - 40} {conf.size.height - 40}, {conf.size.width - 40} {conf.size.height - 30}"/>
    </g>
    </svg>
    """
