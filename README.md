# Text Extractor

Desktop application for extracting text from images using OCR (Optical Character Recognition).

## Features

- Extract text from clipboard images (including images copied from Telegram)
- Load images from files
- Support for multiple languages and LaTeX formulas
- Text formatting options (for regular text)
- Copy extracted text to clipboard
- Clean and simple user interface
- LaTeX formula recognition using pix2tex

## Languages

The choice of languages is limited only by the Tesseract language models; there is an example in languages.json on how to add new languages. Additionally, the application supports LaTeX formula recognition mode.

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
  - pix2tex (for LaTeX formula recognition)

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
2. Select the recognition mode (regular text language or LaTeX) from the dropdown
3. Click "Paste from clipboard" or "Load image" depending on your source
4. Wait for the text to be extracted
5. For regular text mode, use the formatting button to clean up the text if needed
6. For LaTeX mode, the recognized formula will be displayed and can be copied directly
