import argparse
from config import Args
from output_generators import write_html, write_svgs


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
        "--html",
        dest="printer",
        action="store_const",
        help="generate printable html instead of pdf",
        const=write_html,
        default=write_svgs,
    )
    parser.add_argument(
        "--ui",
        type=str,
        choices=["cmd", "streamlit", "gui"],
        default="gui",
        help="Choose UI type (default: gui)",
    )

    return parser.parse_args()
