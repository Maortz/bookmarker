from src.api import start_service
from src.cli import parse_args
from src.core import run_from_file
from src.gui import launch_gui

if __name__ == "__main__":
    import sys

    args = parse_args()

    if args.mode == "gui":
        launch_gui()
    elif args.mode == "srv":
        start_service()
    else:
        if not args.input or not args.out:
            print("Error: --input and --out are required when not using UI")
            sys.exit(1)
        run_from_file(args)
