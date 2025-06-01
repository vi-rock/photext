import flet as ft
from PIL import Image
import easyocr
import pyperclip
from PIL import ImageGrab
import re
import os
import json
from pathlib import Path
from pix2tex.cli import LatexOCR

# Initialize EasyOCR readers for different languages
# We'll initialize them lazily to avoid loading all models at startup
_easyocr_readers = {}


def get_easyocr_reader(lang_codes):
    """Get or create EasyOCR reader for specified language codes"""
    # Convert list to tuple for use as dictionary key
    if isinstance(lang_codes, list):
        key = tuple(lang_codes)
    else:
        key = (lang_codes,)

    if key not in _easyocr_readers:
        # Skip LaTeX as it's handled separately
        if 'latex' in lang_codes:
            return None

        print(f"Инициализация модели распознавания для языков: {lang_codes}")
        _easyocr_readers[key] = easyocr.Reader(lang_codes, gpu=False)
        print("Модель загружена успешно!")

    return _easyocr_readers[key]

# pytesseract.pytesseract.tesseract_cmd = "tesseract.exe"  # Укажите путь к tesseract.exe, если он не в PATH


def remove_hyphen_linebreaks(text: str) -> str:
    # Ищем дефис на конце строки, за которым идёт перенос строки, и склеиваем слова
    # Заменяем шаблон: дефис + перенос строки + возможные пробелы
    # на пустую строку (т.е. удаляем дефис и перенос)
    return re.sub(r'-\s*\n\s*', '', text)


def format_text(text: str, lang_codes) -> str:
    # Don't format LaTeX formulas
    if isinstance(lang_codes, list) and "latex" in lang_codes:
        return text.strip()

    # Regular text formatting
    # Убираем лишние переносы строк
    text = remove_hyphen_linebreaks(text)
    text = text.replace('\n', ' ').strip()

    # Заменим множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)

    # Разбиваем на предложения, делаем capitalize
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip().capitalize() for s in sentences if s.strip()]

    return ' '.join(sentences)


def extract_latex_from_image(img) -> str:
    """
    Извлекает LaTeX из изображения с помощью pix2tex.
    """
    try:
        model = LatexOCR()
        result = model(img)
        if result:
            return result
        else:
            return "Не удалось распознать LaTeX."
    except Exception as e:
        return f"Ошибка при распознавании LaTeX: {str(e)}"


def extract_text_from_image(img, lang_codes) -> str:
    if isinstance(lang_codes, list) and "latex" in lang_codes:
        return extract_latex_from_image(img)
    else:
        try:
            reader = get_easyocr_reader(lang_codes)
            if reader is None:  # LaTeX case
                return extract_latex_from_image(img)

            # Convert PIL Image to numpy array if needed
            import numpy as np
            if hasattr(img, 'mode'):  # PIL Image
                img_array = np.array(img)
            else:
                img_array = img

            # Extract text using EasyOCR
            results = reader.readtext(img_array)

            # Combine all detected text
            extracted_text = ""
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter out low-confidence detections
                    extracted_text += text + " "

            return extracted_text.strip() if extracted_text else "Текст не обнаружен"

        except Exception as e:
            return f"Ошибка при распознавании текста: {str(e)}"


def convert_to_rgb(image: Image.Image) -> Image.Image:
    """
    Приводит изображение к пригодному формату для OCR.
    Убирает альфа-канал, приводит к RGB и применяет предобработку для улучшения распознавания.
    """
    try:
        if not isinstance(image, Image.Image):
            raise TypeError("Input must be a PIL Image object")

        if not hasattr(image, 'size') or not image.size:
            raise ValueError("Image has no size")

        # Конвертируем в RGB, обрабатывая различные форматы
        if image.mode in ("RGBA", "LA"):
            # Создаем новый белый фон
            background = Image.new("RGB", image.size, (255, 255, 255))
            # Накладываем изображение с учетом прозрачности
            if image.mode == "RGBA":
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image, mask=image.split()[1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size
        if width > 4000 or height > 4000:
            ratio = min(4000/width, 4000/height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        elif width < 400 or height < 400:
            ratio = max(400/width, 400/height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Проверяем, что изображение не пустое
        if not image.getbbox():
            raise ValueError("Image is empty")

        # Создаем новое изображение, чтобы убедиться в целостности данных
        verified_image = Image.new("RGB", image.size, (255, 255, 255))
        verified_image.paste(image)

        return verified_image

    except Exception as e:
        raise TypeError(f"Failed to process image: {str(e)}")


def get_image_from_clipboard_common():
    img = ImageGrab.grabclipboard()

    if isinstance(img, Image.Image):
        return convert_to_rgb(img)

    # Если буфер содержит байты
    if isinstance(img, list):
        for item in img:
            if hasattr(item, "read"):
                try:
                    return convert_to_rgb(Image.open(item))
                except Exception as e:
                    print("Ошибка чтения изображения из байтов:", e)

    raise ValueError("Буфер обмена не содержит поддерживаемого изображения")


def load_language_config():
    """
    Загружает конфигурацию языков из файла config/languages.json
    Возвращает список языков и индекс языка по умолчанию
    """
    try:
        config_path = Path(__file__).parent.parent / \
            "config" / "languages.json"
        if not config_path.exists():
            return [
                {"code": ["ru"], "name": "Русский"},
                {"code": ["en"], "name": "English"},
                {"code": ["ru", "en"], "name": "Русский + English"},
                {"code": ["latex"], "name": "LaTeX"}
            ], 2  # Default to "Русский + English"

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            languages = config["languages"]
            default_index = config["default_index"]

            return languages, default_index
    except Exception as e:
        print(f"Ошибка загрузки конфигурации языков: {e}")
        return [
            {"code": ["ru"], "name": "Русский"},
            {"code": ["en"], "name": "English"},
            {"code": ["ru", "en"], "name": "Русский + English"},
            {"code": ["latex"], "name": "LaTeX"}
        ], 2


def get_selected_language_codes(languages, dropdown_value):
    """Get language codes for selected dropdown index"""
    try:
        index = int(dropdown_value)
        if 0 <= index < len(languages):
            return languages[index]["code"]
        return ["en"]  # fallback
    except (ValueError, IndexError):
        return ["en"]  # fallback


def main(page: ft.Page):
    page.title = "Text Extractor"
    page.scroll = "auto"
    page.window.width = 800
    page.window.height = 600
    page.update()

    current_image = {"image": None}

    text_output = ft.TextField(
        label="Распознанный текст",
        multiline=True,
        min_lines=5,
        max_lines=20,
        text_size=16,  # Larger text size for better formula visibility
    )

    def update_ui_for_mode(selected_index: str):
        lang_codes = get_selected_language_codes(languages, selected_index)
        is_latex = "latex" in lang_codes
        format_text_button.visible = not is_latex
        text_output.label = "Распознанная формула LaTeX" if is_latex else "Распознанный текст"
        page.update()

    def on_lang_change(e):
        update_ui_for_mode(lang_dropdown.value)
        if current_image["image"] is not None:
            retry_recognition(None)

    def retry_recognition(e):
        if current_image["image"] is None:
            text_output.value = "Сначала загрузите изображение."
            page.update()
            return

        lang_codes = get_selected_language_codes(
            languages, lang_dropdown.value)
        text_output.value = extract_text_from_image(
            current_image["image"], lang_codes)
        page.update()

    preview_image = ft.Image(
        width=600,
        height=400,
        fit=ft.ImageFit.CONTAIN,
    )

    thumbnail = ft.Image(
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
        visible=False,
    )

    # Preview dialog functions
    def close_preview(e):
        preview_dialog.visible = False
        page.update()

    def show_preview(e):
        preview_dialog.visible = True
        page.update()

    # Modal dialog for preview
    preview_dialog = ft.Container(
        visible=False,
        bgcolor="#000000DE",
        # width=page.window.width,
        # height=page.window.height,
        content=ft.Stack([
            ft.Container(
                content=preview_image,
                alignment=ft.alignment.center,),
            ft.Container(content=ft.IconButton(
                icon="close",
                icon_color="white",
                on_click=close_preview
            ),
                alignment=ft.alignment.top_right,
                margin=10,
            )
        ]),
        alignment=ft.alignment.center,
    )
    thumbnail_button = ft.ElevatedButton(
        text="Просмотр фотографии",
        content=thumbnail,
        on_click=show_preview,
        style=ft.ButtonStyle(
            padding=ft.padding.all(0),
            bgcolor="transparent",
            shape=ft.RoundedRectangleBorder(radius=5),
        )
    )
    thumbnail_container = ft.Container(
        content=thumbnail_button,
        visible=False,
        border=ft.border.all(1, "#CCCCCC"),
        border_radius=5,
        padding=3
    )

    def update_preview_images(img: Image.Image):
        thumb = img.copy()
        preview = img.copy()

        thumb.thumbnail((100, 100))

        # Convert PIL images to base64 for flet
        import io
        import base64

        thumb_bytes = io.BytesIO()
        thumb.save(thumb_bytes, format='PNG')
        thumb_bytes.seek(0)
        thumb_base64 = base64.b64encode(thumb_bytes.getvalue()).decode()

        preview_bytes = io.BytesIO()
        preview.save(preview_bytes, format='PNG')
        preview_bytes.seek(0)
        preview_base64 = base64.b64encode(preview_bytes.getvalue()).decode()

        thumbnail.src_base64 = thumb_base64
        preview_image.src_base64 = preview_base64

        thumbnail.visible = True
        thumbnail_container.visible = True
        page.update()

    def paste_from_clipboard(e):
        try:
            img = get_image_from_clipboard_common()
            update_preview_images(img)
            current_image["image"] = img
        except (ValueError, TypeError) as ve:
            text_output.value = str(ve)
            page.update()
            return

        lang_codes = get_selected_language_codes(
            languages, lang_dropdown.value)
        extracted_text = extract_text_from_image(img, lang_codes)
        text_output.value = extracted_text
        page.update()

    def pick_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            image_path = e.files[0].path
            img = Image.open(image_path)
            update_preview_images(img)
            current_image["image"] = img
            lang_codes = get_selected_language_codes(
                languages, lang_dropdown.value)
            extracted_text = extract_text_from_image(img, lang_codes)
            text_output.value = extracted_text
            page.update()

    def format_text_click(e):
        if text_output.value.strip():
            lang_codes = get_selected_language_codes(
                languages, lang_dropdown.value)
            text_output.value = format_text(text_output.value, lang_codes)
        else:
            text_output.value = "Сначала распознайте текст."
        page.update()

    format_text_button = ft.ElevatedButton(
        "Форматировать текст",
        on_click=format_text_click
    )

    def copy_to_clipboard(e):
        pyperclip.copy(text_output.value)

    def clear_text(e):
        text_output.value = ""
        text_output.update()

    clear_btn = ft.ElevatedButton(
        "Очистить", on_click=lambda e: clear_text(e))
    file_picker = ft.FilePicker(on_result=pick_file_result)
    page.overlay.append(file_picker)
    page.overlay.append(preview_dialog)

    languages, default_lang = load_language_config()

    lang_dropdown = ft.Dropdown(
        label="Язык распознавания",
        options=[ft.dropdown.Option(str(i), text=lang["name"])
                 for i, lang in enumerate(languages)],
        value=str(default_lang),
        width=200
    )

    lang_dropdown.on_change = on_lang_change

    page.add(
        ft.Column([
            ft.Row(
                controls=[
                    lang_dropdown,
                    ft.ElevatedButton(
                        "Вставить из буфера",
                        on_click=paste_from_clipboard
                    ),
                    ft.ElevatedButton(
                        "Загрузить изображение",
                        on_click=lambda _: file_picker.pick_files()
                    ),
                    thumbnail_container
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            ),
            text_output,
            ft.Row(
                [
                    format_text_button,
                    ft.ElevatedButton(
                        "Скопировать текст",
                        on_click=copy_to_clipboard
                    ),
                    ft.ElevatedButton(
                        "Повторить распознавание",
                        on_click=retry_recognition
                    ),
                    clear_btn
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            )
        ])
    )


ft.app(target=main, assets_dir="assets")
