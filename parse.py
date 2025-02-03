import os
import ast
import json


def get_module_info(module_path):
    """Парсит Python-модуль и извлекает информацию о нем."""
    with open(module_path, "r", encoding="utf-8") as f:
        module_content = f.read()

    meta_info = {"pic": None, "banner": None}
    for line in module_content.split("\n"):
        if line.startswith("# meta"):
            key, value = line.replace("# meta ", "").split(": ")
            meta_info[key] = value

    tree = ast.parse(module_content)

    def get_decorator_names(decorator_list):
        return [ast.unparse(decorator) for decorator in decorator_list]

    def extract_loader_command_args(decorator):
        """Извлекает аргументы `ru_doc` и `en_doc` из `@loader.command`."""
        if (
            isinstance(decorator, ast.Call)
            and hasattr(decorator.func, "attr")
            and decorator.func.attr == "command"
        ):
            ru_doc = None
            en_doc = None
            for keyword in decorator.keywords:
                if keyword.arg == "ru_doc":
                    ru_doc = ast.literal_eval(keyword.value)
                elif keyword.arg == "en_doc":
                    en_doc = ast.literal_eval(keyword.value)
            return ru_doc, en_doc
        return None, None

    result = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            decorators = get_decorator_names(node.decorator_list)
            is_tds_mod = [d for d in decorators if "loader.tds" in d]
            if "Mod" not in node.name and not is_tds_mod:
                continue

            class_docstring = ast.get_docstring(node)
            class_info = {
                "name": node.name,
                "description": class_docstring,
                "meta": meta_info,
                "commands": [],
            }

            for class_body_node in node.body:
                if isinstance(class_body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    decorators = get_decorator_names(class_body_node.decorator_list)
                    is_loader_command = [d for d in decorators if "command" in d]
                    if not is_loader_command and "cmd" not in class_body_node.name:
                        continue

                    method_docstring = ast.get_docstring(class_body_node)
                    command_name = class_body_node.name
                    ru_doc, en_doc = None, None

                    # Проверяем каждый декоратор на наличие ru_doc и en_doc
                    for decorator in class_body_node.decorator_list:
                        ru_doc_tmp, en_doc_tmp = extract_loader_command_args(decorator)
                        if ru_doc_tmp:
                            ru_doc = ru_doc_tmp
                        if en_doc_tmp:
                            en_doc = en_doc_tmp

                    # Формируем описание команды
                    descriptions = []
                    if method_docstring:
                        descriptions.append(method_docstring)
                    if ru_doc:
                        descriptions.append(f"RU: {ru_doc}")
                    if en_doc:
                        descriptions.append(f"EN: {en_doc}")

                    class_info["commands"].append(
                        {command_name: " | ".join(descriptions)}
                    )

            result = class_info

    return result


modules_data = {}
base_dir = os.getcwd()

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            try:
                module_info = get_module_info(file_path)
                if module_info:
                    relative_path = os.path.relpath(file_path, base_dir)
                    modules_data[relative_path] = module_info
            except Exception as e:
                print(f"Ошибка при парсинге файла {file_path}: {e}")

with open("modules.json", "w", encoding="utf-8") as json_file:
   json.dump(modules_data, json_file, ensure_ascii=False, indent=2)

print("Файл modules.json создан!")
