import os
import json
import re

def replace_urls_in_file(file_path, libraries):
    """Обновляет URL в одном файле, сохраняя форматирование и скобки."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Проходим по всем URL из libraries и заменяем их
        modified = False
        for old_url, filename in libraries.items():
            new_url = f"git.vsecoder.dev/-/raw/main/libs/{filename}"
            # Регулярное выражение для поиска полного вызова self.import_lib
            # Учитываем пробелы, аргументы и закрывающую скобку
            pattern = rf'(self\.import_lib\(\s*["\']{re.escape(old_url)}["\'](?:\s*,\s*[^)]+)?\))'
            if re.search(pattern, content):
                # Заменяем только URL, сохраняя остальную часть вызова
                replacement = rf'self.import_lib("{new_url}"\g<0>'
                content = re.sub(pattern, lambda m: m.group(0).replace(old_url, new_url), content)
                modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Обновлён файл: {file_path}")
        else:
            print(f"Изменений не требуется: {file_path}")

    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}. Пропускаем.")

def replace_urls_in_all_files(base_dir):
    """Обновляет URL во всех .py файлах, игнорируя .venv и __pycache__."""
    try:
        with open("libs/libraries.json", "r", encoding="utf-8") as f:
            libraries = json.load(f)["libraries"]
    except FileNotFoundError:
        print("Файл libs/libraries.json не найден. Выполните parse_libs.py сначала.")
        return

    for root, _, files in os.walk(base_dir):
        # Пропускаем .venv и __pycache__
        if ".venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                replace_urls_in_file(file_path, libraries)

if __name__ == "__main__":
    base_dir = os.getcwd()
    replace_urls_in_all_files(base_dir)