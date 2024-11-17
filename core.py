from config import Args, Config, Size
from utils import read_csv, get_idx
from svg_generator import get_svg_lines


def do(args: Args) -> None:
    config = Config(Config.fix_a4(Size(args.width, args.height)))
    csv = read_csv(args.input)
    idx = get_idx(config, len(csv))
    bookmarks = get_svg_lines(csv, config, idx)
    args.printer(bookmarks, config, idx, args.out)
