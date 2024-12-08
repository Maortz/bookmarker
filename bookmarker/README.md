# 📚 Daily Bookmark Generator

Generate beautiful bookmarks for your daily learning schedule! This tool helps you create customized bookmarks based on your reading plan, with multiple usage options to suit your needs.

Check it out on [render!](https://bookmarkers-service.onrender.com/docs)

## 🌟 Features

- Generate bookmarks in SVG or HTML format
- Customize bookmark dimensions
- CSV-based input for organized reading schedules

## 🚀 Usage Options

### Web Service 🌐

Start the web service:
```bash
cd bookmarker && uvicorn src.main:app --reload
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
3. **Tanah Yomi**: Example of Tanah Yomi Bookmark based on the [Tanah Yomi learning](https://www.tanachyomi.co.il/)

