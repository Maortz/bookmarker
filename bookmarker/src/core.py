from src.config import Args, Config, Row, Size
from src.svg_generator import get_svg_lines
from src.utils import get_idx, parse_csv, read_csv


def from_file(args_input: str) -> list[Row]:
    return read_csv(args_input)


def from_str(args_input: str) -> list[Row]:
    return parse_csv(args_input.splitlines())


def create_bookmark(args: Args) -> None:
    config = Config(Config.fix_a4(Size(args.width, args.height)), args.font_size)
    idx = get_idx(config, len(args.input))
    bookmarks = get_svg_lines(args.input, config, idx)
    args.printer(bookmarks, config, idx, args.out)
