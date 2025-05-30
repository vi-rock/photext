# Text Extractor

Desktop application for extracting text from images using OCR (Optical Character Recognition).

## Features

- Extract text from clipboard images (including images copied from Telegram)
- Load images from files
- Support for multiple languages.
- Text formatting options
- Copy extracted text to clipboard
- Clean and simple user interface

## Languages

The choice of languages is limited only by the Tesseract language models; there is an example in languages.json on how to add new languages.

### Important!
You must have the Tesseract language packages installed in order to use them.

## Requirements

- Python 3.x
- Tesseract OCR engine installed and in PATH
- Required Python packages (install using `pip install -r requirements.txt`):
  - flet
  - Pillow
  - pytesseract
  - pyperclip

## Installation

1. Make sure you have Tesseract OCR installed on your system
2. Clone this repository
3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the application:
```
python src/main.py
```

1. Copy an image to clipboard or prepare an image file
2. Select the recognition language from the dropdown
3. Click "Paste from clipboard" or "Load image" depending on your source
4. Wait for the text to be extracted
5. Use the formatting button to clean up the text if needed
6. Copy the result to clipboard using the "Copy text" button
