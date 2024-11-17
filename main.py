# import subprocess
from gui import launch_gui
from command_line import parse_args
from core import do
# import streamlit_app

if __name__ == "__main__":
    import sys

    args = parse_args()

    if args.ui == "gui":
        launch_gui()
    elif args.ui == "streamlit":
        # subprocess.run(["streamlit", "run", streamlit_app.__file__])
        print("not supported")
    else:
        if not args.input or not args.out:
            print("Error: --input and --out are required when not using UI")
            sys.exit(1)
        do(args)
