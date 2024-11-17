from config import Args, Config, Size
from svg_generator import get_svg_lines
from utils import get_idx, parse_csv, read_csv


def run_from_file(args: Args) -> None:
    config = Config(Config.fix_a4(Size(args.width, args.height)))
    csv = read_csv(args.input)
    idx = get_idx(config, len(csv))
    bookmarks = get_svg_lines(csv, config, idx)
    args.printer(bookmarks, config, idx, args.out)


def run_from_str(args: Args) -> None:
    config = Config(Config.fix_a4(Size(args.width, args.height)))
    csv = parse_csv(args.input)
    idx = get_idx(config, len(csv))
    bookmarks = get_svg_lines(csv, config, idx)
    args.printer(bookmarks, config, idx, args.out)
