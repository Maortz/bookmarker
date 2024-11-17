# 📚 Daily Bookmark Generator

Generate beautiful bookmarks for your daily learning schedule! This tool helps you create customized bookmarks based on your reading plan, with multiple usage options to suit your needs.

## 🌟 Features

- Generate bookmarks in SVG or HTML format
- Customize bookmark dimensions
- Multiple interface options (CLI, GUI, Web Service)
- CSV-based input for organized reading schedules

## 🚀 Usage Options

### 1. Command Line Interface (CLI)

Basic usage:
```bash
python main.py --input your_schedule.csv --out output_directory
```

Options:
- `-i, --input`: Input CSV file (with date and chapter columns)
- `-o, --out`: Output directory
- `-w, --width`: Bookmark width in cm (default: 10)
- `-l, --height`: Bookmark height in cm (default: 15)
- `--html`: Generate printable HTML instead of SVG files
- `--mode`: Choose running mode (cmd/gui/srv)
- `-h, --help`: Help

### 2. Web Service 🌐

Start the web service:
```bash
python main.py --mode srv
```

Available endpoints:
- `POST /bookmarker/html`: Generate bookmarks in HTML format
  - Parameters:
    - `width`: Bookmark width in cm (default: 10)
    - `height`: Bookmark height in cm (default: 15)
    - `csv_file`: Upload your CSV file

- `POST /bookmarker/svgs`: Generate bookmarks in SVG format
  - Parameters: Same as HTML endpoint

The service runs on `http://127.0.0.1:8000`

### 3. Graphical User Interface (GUI) 🖥️

Launch the GUI:
```bash
python main.py --mode gui
```

## 📋 Input Format

The CSV file should contain two columns:
- `date`: Reading date
- `chapter`: Chapter or content for the bookmark

Example:
```csv
date,chapter
2024-01-01,Genesis 1
2024-01-02,Genesis 2
```

## 🎨 Output Options

1. **SVG Files**: Individual SVG files for each bookmark
2. **HTML**: Single HTML file with all bookmarks, ready for printing

## 🛠️ Requirements

- Python 3.x
- FastAPI
- uvicorn

## 📝 Note

Make sure your CSV file is properly formatted and encoded in UTF-8 to ensure correct processing of special characters.