# meta developer: @limokanews

import os
import time
import random
import logging
import html
import json
import asyncio

import aiohttp
from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema
from whoosh.qparser import MultifieldParser, QueryParser, OrGroup
from whoosh.query import FuzzyTerm, Wildcard

from telethon.types import Message
from .. import utils, loader
from ..types import InlineQuery

logger = logging.getLogger("Limoka")


class Search:
    def __init__(self, query: str, ix):
        self.query = query
        self.ix = ix

    def search_module(self, best_match: bool = True):
        with self.ix.searcher() as searcher:
            parser = MultifieldParser(
                ["title", "description", "commands", "command_descriptions"],
                schema=self.ix.schema,
                fieldboosts={"title": 2.0, "description": 1.0, "commands": 1.5, "command_descriptions": 0.8},
                group=OrGroup
            )
            query = parser.parse(self.query)
            results = searcher.search(query, limit=10 if not best_match else 1)

            if not results:
                fuzzy_parser = QueryParser("commands", self.ix.schema)
                fuzzy_query = fuzzy_parser.parse(f"{self.query}~2")
                results = searcher.search(fuzzy_query, limit=10 if not best_match else 1)

            if not results:
                wildcard_parser = QueryParser("commands", self.ix.schema)
                wildcard_query = wildcard_parser.parse(f"*{self.query}*")
                results = searcher.search(wildcard_query, limit=10 if not best_match else 1)

            if results:
                return results[0]["path"] if best_match else {result["path"] for result in results}
            return None


class LimokaAPI:
    async def get_all_modules(self, url: str) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return json.loads(text)
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            logger.error(f"Failed to fetch modules: {e}")
            raise


class LimokaFormatter:
    @staticmethod
    def format_module(module_info, query, prefix, url, strings, emojis):
        commands = LimokaFormatter.generate_commands(module_info, prefix, strings, emojis)
        return strings["found"].format(
            name=html.escape(module_info["name"] or strings["no_info"]),
            query=html.escape(query),
            description=html.escape(module_info["description"] or strings["no_info"]),
            username=html.escape(module_info["meta"].get("developer", "Unknown")),
            commands="".join(commands),
            prefix=prefix,
            url=url,
            module_path=module_info["path"].replace("\\", "/")
        )

    @staticmethod
    def generate_commands(module_info, prefix, strings, emojis):
        commands = []
        for i, func in enumerate(module_info["commands"], 1):
            if i > 9:
                commands.append("...")
                break
            for command, description in func.items():
                emoji = emojis.get(i, "")
                commands.append(
                    strings["command_template"].format(
                        emoji=emoji,
                        prefix=prefix,
                        command=html.escape(command.replace("cmd", "")) if command else "",
                        description=html.escape(description or strings["no_info"])
                    )
                )
        return commands


@loader.tds
class Limoka(loader.Module):
    """Hikka modules are now in one place with easy searching!"""

    strings = {
        "name": "Limoka",
        "wait": "Just wait\n<emoji document_id=5404630946563515782>🔍</emoji> A search is underway among {count} modules for the query: <code>{query}</code>\n\n<i>{fact}</i>",
        "found": "<emoji document_id=5413334818047940135>🔍</emoji> Found the module <b>{name}</b> by query: <b>{query}</b>\n\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Description:</b> {description}\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Developer:</b> {username}\n\n{commands}\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>",
        "command_template": "{emoji} <code>{prefix}{command}</code> {description}\n",
        "emojis": {
            1: "<emoji document_id=5416037945909987712>1️⃣</emoji>",
            2: "<emoji document_id=5413855071731470617>2️⃣</emoji>",
            3: "<emoji document_id=5416068826724850291>3️⃣</emoji>",
            4: "<emoji document_id=5415843998071803071>4️⃣</emoji>",
            5: "<emoji document_id=5415684843763686989>5️⃣</emoji>",
            6: "<emoji document_id=5415975458430796879>6️⃣</emoji>",
            7: "<emoji document_id=5415769763857060166>7️⃣</emoji>",
            8: "<emoji document_id=5416006506749383505>8️⃣</emoji>",
            9: "<emoji document_id=5415963015910544694>9️⃣</emoji>",
        },
        "404": "<emoji document_id=5210952531676504517>❌</emoji> <b>Not found by query: <i>{query}</i></b>",
        "noargs": "<emoji document_id=5210952531676504517>❌</emoji> <b>No args</b>",
        "?": "<emoji document_id=5951895176908640647>🔎</emoji> Request too short / not found",
        "no_info": "No information",
        "facts": [
            "<emoji document_id=5472193350520021357>🛡</emoji> The limoka catalog is carefully moderated!",
            "<emoji document_id=5940434198413184876>🚀</emoji> Limoka performance allows you to search for modules quickly!",
        ],
        "inline404": "Not found",
        "inline?": "Request too short / not found",
        "inlinenoargs": "Please, enter query",
    }

    strings_ru = {
        "wait": "Подождите\n<emoji document_id=5404630946563515782>🔍</emoji> Идёт поиск среди {count} модулей по запросу: <code>{query}</code>\n\n<i>{fact}</i>",
        "found": "<emoji document_id=5413334818047940135>🔍</emoji> Найден модуль <b>{name}</b> по запросу: <b>{query}</b>\n\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Описание:</b> {description}\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Разработчик:</b> {username}\n\n{commands}\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>",
        "command_template": "{emoji} <code>{prefix}{command}</code> {description}\n",
        "404": "<emoji document_id=5210952531676504517>❌</emoji> <b>Не найдено по запросу: <i>{query}</i></b>",
        "noargs": "<emoji document_id=5210952531676504517>❌</emoji> <b>Нет аргументов</b>",
        "?": "<emoji document_id=5951895176908640647>🔎</emoji> Запрос слишком короткий / не найден",
        "no_info": "Нет информации",
        "facts": [
            "<emoji document_id=5472193350520021357>🛡</emoji> Каталог лимоки тщательно модерируется!",
            "<emoji document_id=5940434198413184876>🚀</emoji> Производительность лимоки позволяет вам искать модули с невероятной скоростью",
        ],
        "inline404": "Не найдено",
        "inline?": "Запрос слишком короткий / не найден",
        "inlinenoargs": "Введите запрос",
    }

    def __init__(self):
        self.api = LimokaAPI()
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "limoka_url",
                "https://git.vsecoder.dev/root/limoka/-/raw/main/",
                "Mirror: https://raw.githubusercontent.com/MuRuLOSE/limoka-mirror/refs/heads/main/",
                validator=loader.validators.String(),
            )
        )
        self.name = self.strings["name"]
        self.schema = Schema(
            title=TEXT(stored=True, field_boost=2.0),
            path=ID(stored=True),
            description=TEXT(stored=True),
            commands=TEXT(stored=True),
            command_descriptions=TEXT(stored=True)
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.modules_cache = await self._fetch_and_cache_modules()
        await asyncio.to_thread(self._init_search_index)

    async def _fetch_and_cache_modules(self):
        modules = await self.api.get_all_modules(self.config["limoka_url"] + "modules.json")
        for path, data in modules.items():
            data["path"] = path
        self.modules_last_updated = time.time()
        return modules

    def _init_search_index(self):
        if not os.path.exists("limoka_search"):
            os.makedirs("limoka_search")
        self.ix = create_in("limoka_search", self.schema)
        writer = self.ix.writer()
        for path, data in self.modules_cache.items():
            name = data.get("name", "") or ""
            description = data.get("description", "") or ""
            commands = " ".join([cmd for func in data.get("commands", []) for cmd in func.keys() if cmd is not None] or [""])
            command_descriptions = " ".join([desc for func in data.get("commands", []) for desc in func.values() if desc is not None] or [""])
            
            writer.add_document(
                title=name,
                path=path,
                description=description,
                commands=commands,
                command_descriptions=command_descriptions
            )
        writer.commit()

    @loader.command()
    async def limokacmd(self, message: Message):
        """[query] - Search module"""
        args = utils.get_args_raw(message)

        if len(args) <= 1:
            return await utils.answer(message, self.strings["?"])
        if not args:
            return await utils.answer(message, self.strings["noargs"])

        await utils.answer(
            message,
            self.strings["wait"].format(
                count=len(self.modules_cache),
                query=html.escape(args),
                fact=random.choice(self.strings["facts"])
            )
        )

        searcher = Search(args.lower(), self.ix)
        result = searcher.search_module()
        if not result:
            return await utils.answer(message, self.strings["404"].format(query=html.escape(args)))

        module_info = self.modules_cache[result]
        try:
            banner = module_info["meta"]["banner"]
            await utils.answer_file(
                message,
                banner,
                LimokaFormatter.format_module(
                    module_info, args, self.get_prefix(), self.config["limoka_url"],
                    self.strings, self.strings["emojis"]
                )
            )
        except Exception:
            await utils.answer(
                message,
                LimokaFormatter.format_module(
                    module_info, args, self.get_prefix(), self.config["limoka_url"],
                    self.strings, self.strings["emojis"]
                )
            )

    @loader.inline_handler()
    async def limoka(self, query: InlineQuery):
        """[query] - Inline search modules"""
        if not query.args:
            return {
                "title": "No query",
                "description": self.strings["inlinenoargs"],
                "thumb": "https://img.icons8.com/?size=100&id=NIWYFnJlcBfr&format=png&color=000000",
                "message": self.strings["inlinenoargs"],
            }

        searcher = Search(query.args.lower(), self.ix)
        results = searcher.search_module(best_match=False)

        if not results:
            return {
                "title": "No results",
                "description": self.strings["inline404"],
                "thumb": "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000",
                "message": self.strings["inline404"],
            }

        return [
            {
                "title": utils.escape_html(module_info["name"] or ""),
                "description": utils.escape_html(module_info["description"] or ""),
                "thumb": module_info["meta"].get(
                    "pic", "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000"
                ),
                "photo": module_info["meta"].get(
                    "banner", "https://habrastorage.org/getpro/habr/upload_files/9c7/5fa/c54/9c75fac54ebb0beaf89abd7d86b4787c.jpg"
                ),
                "message": LimokaFormatter.format_module(
                    module_info, query.args, self.get_prefix(), self.config["limoka_url"],
                    self.strings, self.strings["emojis"]
                )
            }
            for path in results
            if (module_info := self.modules_cache.get(path))
        ]