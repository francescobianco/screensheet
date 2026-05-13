# Screensheet

A simple image annotation tool for GNOME, inspired by GNOME Image Viewer.

## Features

- Open and view images
- Annotate with arrows, lines, rectangles, free drawing, and text
- Save annotated images
- Keyboard shortcuts (Ctrl+O to open, Ctrl+S to save, Ctrl+Z to undo)

## Requirements

- Python 3
- GTK 4
- PyGObject
- cairo

## Installation

```bash
# Install dependencies (Fedora)
sudo dnf install python3-gobject python3-cairo gtk4

# Install dependencies (Ubuntu/Debian)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Run
python3 screensheet.py
```

## Usage

```bash
# Open the application
python3 screensheet.py

# Open an image directly
python3 screensheet.py image.png
```

## Tools

- **Arrow**: Click and drag to draw arrows
- **Line**: Click and drag to draw lines
- **Rectangle**: Click and drag to draw rectangles
- **Free Draw**: Click and drag to draw freely
- **Text**: Click to place text annotations

## License

MIT License - see LICENSE file for details
