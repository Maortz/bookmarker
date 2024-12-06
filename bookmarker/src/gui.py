import os
import tkinter as tk
from tkinter import filedialog, ttk

from src.config import Args
from src.core import run_from_file
from src.output_generators import write_html, write_svgs


class BookmarkGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Bookmark Generator")

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input file selection
        ttk.Label(main_frame, text="Input CSV File:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=40)
        input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(
            row=0, column=2, pady=5
        )

        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=40)
        output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(
            row=1, column=2, pady=5
        )

        # Width and height inputs
        dimension_frame = ttk.Frame(main_frame)
        dimension_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Label(dimension_frame, text="Width (cm):").grid(row=0, column=0, padx=5)
        self.width = tk.StringVar(value="10")
        ttk.Entry(dimension_frame, textvariable=self.width, width=10).grid(
            row=0, column=1, padx=5
        )

        ttk.Label(dimension_frame, text="Height (cm):").grid(row=0, column=2, padx=5)
        self.height = tk.StringVar(value="15")
        ttk.Entry(dimension_frame, textvariable=self.height, width=10).grid(
            row=0, column=3, padx=5
        )

        # Output type selection
        self.output_type = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame,
            text="Generate printable HTML (instead of SVG files)",
            variable=self.output_type,
        ).grid(row=3, column=0, columnspan=3, pady=10)

        # Generate button
        ttk.Button(main_frame, text="Generate Bookmarks", command=self.generate).grid(
            row=4, column=0, columnspan=3, pady=10
        )

        # Status message
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3
        )

    def browse_input(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)

    def validate_inputs(self) -> tuple[bool, str]:
        # Check if input file is selected and exists
        if not self.input_path.get():
            return False, "Please select an input CSV file"
        if not os.path.exists(self.input_path.get()):
            return False, "Input file does not exist"

        # Check if output directory is selected
        if not self.output_path.get():
            return False, "Please select an output directory"

        # Validate width and height
        try:
            width = int(self.width.get())
            height = int(self.height.get())
            if width <= 0 or height <= 0:
                return False, "Width and height must be positive numbers"
        except ValueError:
            return False, "Width and height must be valid numbers"

        return True, ""

    def generate(self):
        # Validate inputs
        is_valid, message = self.validate_inputs()
        if not is_valid:
            self.status_var.set(f"Error: {message}")
            return

        try:
            # Create args object
            args = Args(
                input=self.input_path.get(),
                out=self.output_path.get(),
                width=int(self.width.get()),
                height=int(self.height.get()),
                font_size=12,
                printer=write_html if self.output_type.get() else write_svgs,
            )

            # Call the do function
            run_from_file(args)

            self.status_var.set("Bookmarks generated successfully!")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")


def launch_gui():
    root = tk.Tk()
    BookmarkGeneratorGUI(root)
    root.mainloop()
