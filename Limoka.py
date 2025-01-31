from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema
from whoosh.qparser import QueryParser, OrGroup
from whoosh.query import FuzzyTerm, Wildcard

import aiohttp
import random
import logging
import os
import re
import html
import json

from telethon.types import Message
from telethon.errors.rpcerrorlist import YouBlockedUserError
from ..inline.types import InlineCall
from .. import utils, loader


logger = logging.getLogger("Limoka")


class Search:
    def __init__(self, query: str):
        self.schema = Schema(
            title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True)
        )
        self.query = query

    def search_module(self, content):
        if not os.path.exists("limoka_search"):
            os.makedirs("limoka_search")

        ix = create_in("limoka_search", self.schema)
        writer = ix.writer()

        # Добавляем документы в индекс
        for module_content in content:
            writer.add_document(
                title=module_content["id"],  # Используем путь как title
                path=module_content["id"],  # Путь — это уникальный идентификатор
                content=module_content["content"],  # Содержимое для поиска
            )
        writer.commit()

        with ix.searcher() as searcher:
            # Парсер для поиска
            parser = QueryParser("content", ix.schema, group=OrGroup)
            query = parser.parse(self.query)

            # Альтернативные запросы (поиск с учетом ошибок и подстановок)
            fuzzy_query = FuzzyTerm("content", self.query, maxdist=1, prefixlength=2)
            wildcard_query = Wildcard("content", f"*{self.query}*")

            # Выполнение поиска
            results = searcher.search(query)

            if not results:
                results = searcher.search(fuzzy_query)
            if not results:
                results = searcher.search(wildcard_query)

            # Возвращаем путь модуля (ключ) или 0, если не найдено
            if results:
                best_match = results[0]
                return best_match["path"]  # Возвращаем путь (ключ) модуля
            else:
                return 0


class LimokaAPI:
    async def get_all_modules(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://git.vsecoder.dev/root/limoka/-/raw/main/modules.json"
            ) as response:
                text = await response.text()
                return json.loads(text)

    async def get_module_raw(self, module_path: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://git.vsecoder.dev/root/limoka/-/raw/main/{module_path}"
            ) as response:
                return await response.text()


@loader.tds
class Limoka(loader.Module):
    """Search modules!"""

    strings = {
        "name": "Limoka",
        "wait": "Just wait" "\n<i>{fact}</i>",
        "found": "<emoji document_id=5188311512791393083>🔎</emoji> Found the module <b>{name}</b> by query: <b>{query}</b>"
        "\n<b>ℹ️ Description:</b> {description}"
        "\n<b><emoji document_id=5190458330719461749>🧑‍💻</emoji> Developer:</b> {username}"  
        "\n\n{commands}"
        "\n<code>.dlm https://git.vsecoder.dev/root/limoka/-/raw/main/{module_path}</code>",
        "command_template": "{emoji} <code>{prefix}{command}</code> - {description}\n",
        "emojis": {
            1: "<emoji document_id=5449498872176983423>1️⃣</emoji>",
            2: "<emoji document_id=5447575603001705541>2️⃣</emoji>",
            3: "<emoji document_id=5447344971847844130>3️⃣</emoji>",
            4: "<emoji document_id=5449783211896879221>4️⃣</emoji>",
            5: "<emoji document_id=5449556257235024153>5️⃣</emoji>",
            6: "<emoji document_id=5449643483725837995>6️⃣</emoji>",
            7: "<emoji document_id=5447255791146910115>7️⃣</emoji>",
            8: "<emoji document_id=5449394534536462346>8️⃣</emoji>",
            9: "<emoji document_id=5447140424030371281>9️⃣</emoji>",
        },
        "404": "<emoji document_id=5210952531676504517>❌</emoji> <b>Not found</b>",
        "noargs": "<emoji document_id=5210952531676504517>❌</emoji> <b>No args</b>",
        "?": "Request too short / not found",
        "no_info": "No information",
    }

    strings_ru = {
        "wait": "Подождите" "\n<i>{fact}</i>",
        "found": "<emoji document_id=5188311512791393083>🔎</emoji> Найден модуль <b>{name}</b> по запросу: <b>{query}</b>"
        "\n<b>ℹ️ Описание:</b> {description}"
        "\n<b><emoji document_id=5190458330719461749>🧑‍💻</emoji> Разработчик:</b> {username}"
        "\n\n{commands}"
        "\n\n<code>.dlm https://git.vsecoder.dev/root/limoka/-/raw/main/{module_path}</code>",
        "command_template": "{emoji} <code>{prefix}{command}</code> - {description}\n",
        "emojis": {
            1: "<emoji document_id=5449498872176983423>1️⃣</emoji>",
            2: "<emoji document_id=5447575603001705541>2️⃣</emoji>",
            3: "<emoji document_id=5447344971847844130>3️⃣</emoji>",
            4: "<emoji document_id=5449783211896879221>4️⃣</emoji>",
            5: "<emoji document_id=5449556257235024153>5️⃣</emoji>",
            6: "<emoji document_id=5449643483725837995>6️⃣</emoji>",
            7: "<emoji document_id=5447255791146910115>7️⃣</emoji>",
            8: "<emoji document_id=5449394534536462346>8️⃣</emoji>",
            9: "<emoji document_id=5447140424030371281>9️⃣</emoji>",
        },
        "404": "<emoji document_id=5210952531676504517>❌</emoji> <b>Не найдено</b>",
        "noargs": "<emoji document_id=5210952531676504517>❌</emoji> <b>Нет аргументов</b>",
        "?": "Запрос слишком короткий / не найден",
        "no_info": "Нет информации",
    }

    async def client_ready(self, client, db):
        self._prefix = self.get_prefix()

    def __init__(self):
        self.api = LimokaAPI()
        self.facts = [
            "The limoka catalog is carefully moderated!",
            "Limoka performance allows you to search for modules quickly!",
        ]

    async def buttons_download(self, module_path, text, message: Message):
        markup = [
            {
                "text": "⬇️ Download",
                "callback": self._inline_download,
                "args": [module_path],
            }
        ]

        return await self.inline.form(
            text,
            message,
            reply_markup=markup,
        )

    @loader.command()
    async def limoka(self, message: Message):
        """[query] - Search module"""
        args = utils.get_args_raw(message)

        await utils.answer(
            message, self.strings["wait"].format(fact=random.choice(self.facts))
        )

        if not args:
            return await utils.answer(message, self.strings["noargs"])

        modules = await self.api.get_all_modules()

        contents = []

        for module_path, module_data in modules.items():
            contents.append(
                {
                    "id": module_path,
                    "content": module_data["name"],
                }
            )

        for module_path, module_data in modules.items():
            contents.append(
                {
                    "id": module_path,
                    "content": module_data["description"],
                }
            )

        for module_path, module_data in modules.items():
            for func in module_data["commands"]:
                for command, description in func.items():
                    contents.append({"id": module_path, "content": command})
                    contents.append({"id": module_path, "content": description})

        searcher = Search(args)
        try:
            result = searcher.search_module(contents)
        except IndexError:
            return await utils.answer(message, self.strings["?"])

        module_path = result

        if module_path == 0:
            await utils.answer(message, self.strings["404"])

        else:
            module_info = modules[module_path]

            dev_username = module_info["meta"]["developer"] if "developer" in module_info["meta"] else "Unknown"

            name = module_info["name"]
            description = module_info["description"]

            commands = []

            command_count = 0
            for func in module_info["commands"]:
                for command, description in func.items():
                    command_count += 1
                    if command_count < 9:
                        commands.append(
                            self.strings["command_template"].format(
                                prefix=self._prefix,
                                command=html.escape(command),
                                emoji=self.strings["emojis"][command_count],
                                description=(
                                    html.escape(description)
                                    if description
                                    else self.strings["no_info"]
                                ),
                            )
                        )
                    else:
                        commands.append("...")

            await utils.answer(
                message,
                self.strings["found"].format(
                    query=args,
                    name=name if name else self.strings["no_info"],
                    description=(
                        html.escape(description)
                        if description
                        else self.strings["no_info"]
                    ),
                    username=dev_username,
                    commands="".join(commands),
                    prefix=self._prefix,
                    module_path=module_path,
                ),
            )

    async def _load_module(self, module_path):
        loader_m = self.lookup("loader")
        module_code = await self.api.get_module_raw(module_path)
        await loader_m.download_and_install(module_code, None)

        if getattr(loader_m, "fully_loaded", False):
            loader_m.update_modules_in_db()

    async def _inline_download(self, call: InlineCall, module_path: str):
        await self._load_module(module_path)

        modules = await self.api.get_all_modules()
        info = modules[module_path]
        markup = [{"text": "❌ Close", "action": "close"}]
        await call.edit(
            f"✔️ Module {info['name']} installed successfully\n\n<code>.help {info['name']}</code>",
            reply_markup=markup,
        )
