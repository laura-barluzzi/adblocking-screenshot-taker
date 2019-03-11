import base64
import json
from PIL import Image
from io import BytesIO
from pathlib import Path


def _add_metatdata(log_file, metadata):
    try:
        with log_file.open('r', encoding='utf-8') as file:
            logs = json.load(file)
    except FileNotFoundError:
        logs = {}

    logs.setdefault("test_metadata", metadata)

    with log_file.open('w', encoding='utf-8') as file:
        json.dump(logs, file)


def _add_url_to_logs(log_file, screenshot_data):
    try:
        with log_file.open('r', encoding='utf-8') as file:
            logs = json.load(file)
    except FileNotFoundError:
        logs = {}

    tests = logs.setdefault("tests", {})

    test = tests.setdefault(screenshot_data["url"], {})

    test[screenshot_data["extension_status"]] = screenshot_data

    with log_file.open('w', encoding='utf-8') as file:
        json.dump(logs, file)


def _assure_directories_exist(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def _take_screenshot(driver, path_to_screenshot):
    screenshot = Image.open(BytesIO(base64.b64decode(driver.get_screenshot_as_base64())))
    width, height = screenshot.size

    body = driver.find_element_by_tag_name('body')
    body_info = body.rect

    left = (width - body_info['width']) // 2
    top = body_info['y']
    right = (left + body_info['width'])
    bottom = height

    cropped_screenshot = screenshot.crop((left, top, right, bottom))
    cropped_screenshot.load()
    cropped_screenshot.save(path_to_screenshot)
