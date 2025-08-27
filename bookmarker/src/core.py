from src.config import Args, PageConfig, Row, Size, Content
from src.svg_generator import get_svg_tables
from src.utils import get_idx, parse_csv, read_csv


def from_file(args_input: str) -> list[Row]:
    return read_csv(args_input)


def from_str(args_input: str) -> list[Row]:
    return parse_csv(args_input.splitlines())


def create_bookmark(args: Args, content: Content) -> None:
    config = PageConfig(PageConfig.fix_a4(Size(args.width, args.height)), args.font_size)
    idx = get_idx(config, len(args.input))
    bookmarks = get_svg_tables(args.input, config, idx)
    args.printer(content, bookmarks, config, args.out)
