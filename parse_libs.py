import os
import ast
import json
import urllib.parse

def extract_import_lib_urls(file_path):
    """Извлекает URL из вызовов self.import_lib в файле."""
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        class ImportLibVisitor(ast.NodeVisitor):

            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'import_lib' and isinstance(node.func.value, ast.Name) and (node.func.value.id == 'self'):
                    if node.args and isinstance(node.args[0], (ast.Str, ast.Constant)):
                        url = node.args[0].s if hasattr(node.args[0], 's') else node.args[0].value
                        if url.startswith('http'):
                            urls.append(url)
                self.generic_visit(node)
        visitor = ImportLibVisitor()
        visitor.visit(tree)
    except Exception as e:
        print(f'Ошибка при парсинге {file_path}: {e}')
    return urls

def parse_all_libraries(base_dir):
    """Собирает все URL библиотек и создаёт маппинг с именами файлов."""
    libraries = {}
    for root, _, files in os.walk(base_dir):
        if '.venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                urls = extract_import_lib_urls(file_path)
                for url in urls:
                    filename = urllib.parse.urlparse(url).path.split('/')[-1]
                    libraries[url] = filename
    return libraries
if __name__ == '__main__':
    base_dir = os.getcwd()
    libraries = parse_all_libraries(base_dir)
    os.makedirs('libs', exist_ok=True)
    with open('libs/libraries.json', 'w', encoding='utf-8') as f:
        json.dump({'libraries': libraries}, f, ensure_ascii=False, indent=2)
    print(f'Найдено {len(libraries)} библиотек. Сохранено в libs/libraries.json')