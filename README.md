# ScreenLog Tool

A simple desktop application to capture screenshots of a user-defined area at a set interval (default 500ms). Built with Python and PyQt6.

## Features
- **Custom Area Selection**: Draw a rectangle screen to define the capture region.
- **Automated Capture**: Automatically saves screenshots every 500ms.
- **Background Operation**: Runs efficiently in the background.
- **Timestamped Files**: Saves images with high-precision timestamps.

## Prerequisites
- Python 3.9+
- macOS (tested), Window, or Linux

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python main.py
```
(Or `python3 main.py` depending on your environment)

2. **Select Area**: Click the "Select Area" button. The screen will dim. Click and drag to draw a red rectangle around the area you want to capture. Press `Esc` to cancel.
3. **Start Capture**: Click "Start Capture". The status will change to "Capturing...", and screenshots will be saved to the `captures/` directory.
4. **Stop Capture**: Click "Stop Capture" to end the session.

## Output
Screenshots are saved in the `captures/` folder in the project directory with the format:
`capture_YYYYMMDD_HHMMSS_ffffff.png`

## Troubleshooting

### "ModuleNotFoundError: No module named '_tkinter'""
If you see this error, it means your Python installation is missing Tkinter. This project now uses **PyQt6** to avoid this issue. Please ensure you have installed the requirements:
```bash
pip install -r requirements.txt
```
And that you are running the latest version of the code.
