import os
import aiohttp
import hashlib
import json
import asyncio

async def download_with_integrity_check(url: str, local_path: str) -> bool:
    """Скачивает файл с проверкой целостности, возвращает True, если файл обновлён."""
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    meta_path = f'{local_path}.meta.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Не удалось скачать {url}: {response.status}')
                return False
            content = await response.read()
            current_hash = hashlib.sha256(content).hexdigest()
    if os.path.exists(local_path) and os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        if meta.get('hash') == current_hash:
            print(f'Файл {local_path} актуален')
            return False
    with open(local_path, 'wb') as f:
        f.write(content)
    with open(meta_path, 'w') as f:
        json.dump({'hash': current_hash, 'url': url}, f)
    print(f'Обновлён файл: {url} -> {local_path}')
    return True

async def update_libraries():
    """Обновляет все библиотеки из libs/libraries.json."""
    if not os.path.exists('libs/libraries.json'):
        print('Файл libs/libraries.json не найден. Сначала выполните парсинг.')
        return
    with open('libs/libraries.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        libraries = data.get('libraries', {})
    tasks = []
    for url, filename in libraries.items():
        local_path = f'libs/{filename}'
        tasks.append(download_with_integrity_check(url, local_path))
    results = await asyncio.gather(*tasks)
    if any(results):
        print('Найдены обновления библиотек')
    else:
        print('Все библиотеки актуальны')
if __name__ == '__main__':
    asyncio.run(update_libraries())