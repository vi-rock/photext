# Text Extractor

Desktop application for extracting text from images using advanced OCR (Optical Character Recognition) with neural networks.

## Features

- 🖼️ Extract text from clipboard images (including images copied from Telegram)
- 📁 Load images from files
- 🌍 Support for 80+ languages with EasyOCR neural networks
- 🧮 LaTeX formula recognition using pix2tex
- ✨ Text formatting options (for regular text)
- 📋 Copy extracted text to clipboard
- 🎨 Clean and modern user interface
- 🚀 No external dependencies - pure Python solution

## Languages

The application uses EasyOCR neural networks which support over 80 languages out of the box. You can configure available languages in `config/languages.json`. The application supports:

- **Russian** - for Cyrillic text
- **English** - for Latin text  
- **Russian + English** - for mixed text (default)
- **LaTeX** - for mathematical formulas

### Supported Languages by EasyOCR
Includes but not limited to: English, Russian, Chinese, Japanese, Korean, German, French, Spanish, Italian, Portuguese, Arabic, Hindi, Thai, Vietnamese, and many more.

## Requirements

- Python 3.8+
- Required Python packages (install using `pip install -r requirements.txt`):
  - flet (UI framework)
  - easyocr (neural OCR engine)
  - Pillow (image processing)
  - pyperclip (clipboard operations)
  - pix2tex (LaTeX formula recognition)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: On first run, EasyOCR will automatically download the required neural network models (~100MB). This only happens once.

## Usage

Run the application:
```bash
python src/main.py
```

## Configuration

Edit `config/languages.json` to customize available languages:

```json
{
    "languages": [
        {
            "code": ["ru"],
            "name": "Русский"
        },
        {
            "code": ["en"],
            "name": "English"
        },
        {
            "code": ["ru", "en"],
            "name": "Русский + English"
        },
        {
            "code": ["latex"],
            "name": "LaTeX"
        }
    ],
    "default": ["ru", "en"]
}
```

## Troubleshooting

- **First run is slow**: EasyOCR downloads models on first use (~100MB)
- **Poor recognition**: Try different language settings or higher quality images
- **Memory issues**: Models are cached per language combination
- **GPU errors**: The app automatically falls back to CPU mode