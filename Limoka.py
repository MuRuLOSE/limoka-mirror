# meta developer: @limokanews

from whoosh.index import create_in
from whoosh.fields import TEXT, ID, Schema
from whoosh.qparser import QueryParser, OrGroup
from whoosh.query import FuzzyTerm, Wildcard

import aiohttp
import random
import logging
import os
import html
import json

from telethon.types import Message
from .. import utils, loader
from ..types import InlineQuery


logger = logging.getLogger("Limoka")


class Search:
    def __init__(self, query: str):
        self.schema = Schema(
            title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True)
        )
        self.query = query

    def search_module(self, content, best_match: bool = True):
        if not os.path.exists("limoka_search"):
            os.makedirs("limoka_search")

        ix = create_in("limoka_search", self.schema)
        writer = ix.writer()

        for module_content in content:
            writer.add_document(
                title=module_content["id"],
                path=module_content["id"],
                content=module_content["content"],
            )
        writer.commit()

        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema, group=OrGroup)
            query = parser.parse(self.query)

            fuzzy_query = FuzzyTerm("content", self.query, maxdist=1, prefixlength=2)
            wildcard_query = Wildcard("content", f"*{self.query}*")

            results = searcher.search(query)

            if not results:
                results = searcher.search(fuzzy_query)
            if not results:
                results = searcher.search(wildcard_query)

            if results:
                if best_match:
                    best_match = results[0]
                    return best_match["path"]
                else:
                    return set([result["path"] for result in results])
            else:
                return 0


class LimokaAPI:
    async def get_all_modules(self, url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                return json.loads(text)


@loader.tds
class Limoka(loader.Module):
    """Hikka modules are now in one place with easy searching!"""

    strings = {
        "name": "Limoka",
        "wait": (
            "Just wait"
            "\n<emoji document_id=5404630946563515782>🔍</emoji> A search is underway among {count} modules for the query: <code>{query}</code>"
            "\n"
            "\n<i>{fact}</i>"
        ),
        "found": (
            "<emoji document_id=5413334818047940135>🔍</emoji> Found the module <b>{name}</b> by query: <b>{query}</b>"
            "\n"
            "\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Description:</b> {description}"
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Developer:</b> {username}"
            "\n\n{commands}"
            "\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm https://git.vsecoder.dev/root/limoka/-/raw/main/{module_path}</code>"
        ),
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
        "wait": (
            "Подождите"
            "\n<emoji document_id=5404630946563515782>🔍</emoji> Идёт поиск среди {count} модулей по запросу: <code>{query}</code>"
            "\n"
            "\n<i>{fact}</i>"
        ),
        "found": (
            "<emoji document_id=5413334818047940135>🔍</emoji> Найден модуль <b>{name}</b> по запросу: <b>{query}</b>"
            "\n"
            "\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Описание:</b> {description}"
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Разработчик:</b> {username}"
            "\n"
            "\n{commands}"
            "\n"
            "\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm https://git.vsecoder.dev/root/limoka/-/raw/main/{module_path}</code>"
        ),
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

    def translate_description(self, command):
        user_lang = self._db.get("hikka.translations", "lang", "en")[0:2]

        descriptions = {}

        for lang, description in command.items():
            if description:
                descriptions.update({lang[0:2]: description})

        return descriptions[user_lang]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    def __init__(self):
        self.api = LimokaAPI()
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "limoka_url",
                "https://git.vsecoder.dev/root/limoka/-/raw/main/modules.json",
                "Mirror: https://raw.githubusercontent.com/MuRuLOSE/limoka-mirror/refs/heads/main/modules.json",
                validator=loader.validators.String(),
            )
        )
        self.name = self.strings["name"]

    def generate_commands(self, module_info):
        commands = []
        command_count = 0
        end_count_cmds = False

        for func in module_info["commands"]:
            if end_count_cmds:
                break
            for command, description in func.items():
                if command_count == 9:
                    commands.append("...")
                    end_count_cmds = True
                    break
                command_count += 1
                emoji = self.strings["emojis"].get(command_count, "")
                commands.append(
                    self.strings["command_template"].format(
                        prefix=self.get_prefix(),
                        command=html.escape(command.replace("cmd", "")),
                        emoji=emoji,
                        description=(
                            html.escape(description)
                            if description
                            else self.strings["no_info"]
                        ),
                    )
                )

        return commands

    @loader.command()
    async def limokacmd(self, message: Message):
        """[query] - Search module"""
        args = utils.get_args_raw(message)

        if len(args) <= 1:
            return await utils.answer(message, self.strings["?"])

        if not args:
            return await utils.answer(message, self.strings["noargs"])

        modules = await self.api.get_all_modules(self.config["limoka_url"])

        await utils.answer(
            message,
            self.strings["wait"].format(
                count=len(modules),
                fact=random.choice(self.strings["facts"]),
                query=args,
            ),
        )

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

        searcher = Search(args.lower())
        try:
            result = searcher.search_module(contents)
        except IndexError:
            return await utils.answer(message, self.strings["?"])

        module_path = result

        if module_path is None or module_path == 0:
            return await utils.answer(message, self.strings["404"].format(query=args))

        module_info = modules[module_path]

        dev_username = module_info["meta"].get("developer", "Unknown")

        name = module_info["name"]
        description = (
            html.escape(module_info["description"])
            if module_info["description"]
            else self.strings["no_info"]
        )
        banner = module_info["meta"]["banner"]

        if description:
            translated_desc = await self._client.translate(
                message.peer_id,
                message,
                to_lang=self._db.get("hikka.translations", "lang", "en")[0:2],
                raw_text=description,
                entities=message.entities,
            )

        commands = self.generate_commands(module_info)

        try:
            await utils.answer_file(
                message,
                banner,
                self.strings["found"].format(
                    query=args,
                    name=name if name else self.strings["no_info"],
                    description=(
                        translated_desc if description else self.strings["no_info"]
                    ),
                    username=dev_username,
                    commands="".join(commands),
                    prefix=self.get_prefix(),
                    module_path=module_path.replace("\\", "/"),
                ),
            )
        except Exception:
            await utils.answer(
                message,
                self.strings["found"].format(
                    query=args,
                    name=name if name else self.strings["no_info"],
                    description=(
                        translated_desc if description else self.strings["no_info"]
                    ),
                    username=dev_username,
                    commands="".join(commands),
                    prefix=self.get_prefix(),
                    module_path=module_path,
                ),
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

        modules = await self.api.get_all_modules(self.config["limoka_url"])

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

        searcher = Search(query.args)

        try:
            results = searcher.search_module(contents, best_match=False)
        except IndexError:
            return {
                "title": "Something went wrong...",
                "description": self.strings["inline?"],
                "thumb": "https://img.icons8.com/?size=100&id=rUSWMuGVdxJj&format=png&color=000000",
                "message": self.strings["inline?"],
            }

        if not results:
            return {
                "title": "No results",
                "description": self.strings["inline404"],
                "thumb": "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000",
                "message": self.strings["inline404"],
            }

        return [
            {
                "title": f"{utils.escape_html(module_info['name'])}",
                "description": utils.escape_html(module_info["description"]),
                "thumb": module_info["meta"].get(
                    "pic",
                    "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000",
                ),
                "photo": module_info["meta"].get(
                    "banner",
                    "https://habrastorage.org/getpro/habr/upload_files/9c7/5fa/c54/9c75fac54ebb0beaf89abd7d86b4787c.jpg",
                ),
                "message": self.strings["found"].format(
                    name=module_info["name"],
                    query=query.args,
                    description=module_info["description"],
                    username=module_info["meta"].get("developer", "Unknown"),
                    commands="".join(self.generate_commands(module_info)),
                    module_path=path.replace("\\", "/"),
                    prefix=self.get_prefix(),
                ),
            }
            for path in results
            if (module_info := modules.get(path))
            and (func := module_info.get("commands"))
        ]
