import argparse

from src.config import Args
from src.output_generators import write_html, write_svgs


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="""Daily Bookmark Generator
        Generate a svg bookmark files for daily learning, based on csv file""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="input csv file, organize by date and chapter columns",
        required=False,
    )
    parser.add_argument("--out", "-o", type=str, help="out directory", required=False)
    parser.add_argument(
        "--width", "-w", type=int, help="bookmark width (cm)", default=10
    )
    parser.add_argument(
        "--height", "-l", type=int, help="bookmark height (cm)", default=15
    )
    parser.add_argument(
        "--font-size", type=int, help="font size", default=12
    )
    parser.add_argument(
        "--svg",
        dest="printer",
        action="store_const",
        help="generates multiple svgs files (instead of a printable html)",
        const=write_svgs,
        default=write_html,
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["cmd", "gui", "srv"],
        default="cmd",
        help="Choose running mode (default: cmd)",
    )

    return parser.parse_args()
