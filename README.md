# One-Click Copy Tool

A powerful multi-file one-click copy application that supports opening multiple files simultaneously and quickly copying content.

## Features

- **Multi-file Support**: Open multiple files simultaneously with convenient tab switching
- **Line-by-line Copy**: Each line has its own copy button
- **Batch Copy**:
  - Copy all file contents
  - Merge copy (merge all contents in file order)
  - Separate copy (each file separately, separated by blank lines)
- **Folder Loading**: Support loading all files in a folder with one click
- **File Filtering**: Support selecting specific file types
- **Large File Handling**: Automatically skip files larger than 10MB
- **Error Handling**: Complete handling for permission denied, unsupported encoding, and other errors

## Interface Preview

Light-themed professional interface design, compliant with WCAG AA contrast standards.

## System Requirements

- Python 3.8+
- tkinter (Python standard library)

## Installation and Running

1. Ensure Python 3.8 or higher is installed
2. Run the following command to start the program:

```bash
python copy_app.py
```

## User Guide

### Adding Files
- Click the "Add Files" button to select one or more files
- Click the "Add Folder" button to load all files from a folder

### Copy Operations
- **Single Line Copy**: Click the "Copy" button on the right side of any line
- **Copy All Files**: Copy all file contents to clipboard in sequence
- **Merge Copy**: Choose whether to merge and copy in file order

### Tab Operations
- Click tab names to switch between files
- Click "Close Current" to remove the current file
- Click "Close All" to remove all files

## Project Structure

```
g:\Python_work\
├── copy_app.py           # Main program source code
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── Mods/                 # Sample files folder
```

## Development Notes

When modifying or extending functionality, please ensure:
- Follow the existing code style
- Add appropriate error handling
- Test all functional modules

## License

MIT License