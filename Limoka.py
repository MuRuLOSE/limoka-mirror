from whoosh.index import create_in, open_dir
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
    def __init__(self, query, ix):
        self.schema = Schema(
            title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True)
        )
        self.query = query
        self.ix = ix

    def search_module(self, content=None, best_match=True):
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema, group=OrGroup.factory(0.8))
            query = parser.parse(self.query)

            wildcard_query = Wildcard("content", "*{0}*".format(self.query))
            
            fuzzy_query = FuzzyTerm("content", self.query, maxdist=2, prefixlength=1)

            results = searcher.search(query)

            if not results:
                results = searcher.search(wildcard_query)
            
            if not results:
                results = searcher.search(fuzzy_query)

            if results:
                if best_match:
                    best_match_result = results[0]
                    return best_match_result["path"]
                else:
                    return set([result["path"] for result in results])
            else:
                return 0


class LimokaAPI:
    async def get_all_modules(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                return json.loads(text)
            
    async def get_trusted_developers(self, url):
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
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Developer:</b> {username} {tag}"
            "\n\n{commands}"
            "\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>"
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
        "tag_trust": "<emoji document_id=5411197345968701560>✅</emoji> <a href='https://t.me/limokanews/73'>(what?)</a>",
        "tag_nontrust": "<emoji document_id=5416076321442777828>❌</emoji> <a href='https://t.me/limokanews/73'>(what?)</a>"
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
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Разработчик:</b> {username} {tag}"
            "\n"
            "\n{commands}"
            "\n"
            "\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>"
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
        "tag_trust": "<emoji document_id=5411197345968701560>✅</emoji> <a href='https://t.me/limokanews/73'>(что это?)</a>",
        "tag_nontrust": "<emoji document_id=5416076321442777828>❌</emoji> <a href='https://t.me/limokanews/73'>(что это?)</a>"
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
        self.api = LimokaAPI()

        self.schema = Schema(
            title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True)
        )
        if not os.path.exists("limoka_search"):
            os.makedirs("limoka_search")
        self.ix = (
            create_in("limoka_search", self.schema)
            if not os.path.isdir("limoka_search/index")
            else open_dir("limoka_search")
        )
        self.modules = await self.api.get_all_modules(
            self.config["limoka_url"] + "modules.json"
        )
        self.trusted = await self.api.get_all_modules(
            self.config["limoka_url"] + "trusted.json"
        )
        await self._update_index()

    async def _update_index(self):
        writer = self.ix.writer()

        for module_path, module_data in self.modules.items():
            writer.add_document(
                title=module_path,
                path=module_path,
                content=module_data["name"],
            )
            writer.add_document(
                title=module_path,
                path=module_path,
                content=module_data["description"],
            )
            for func in module_data["commands"]:
                for command, description in func.items():
                    writer.add_document(
                        title=module_path,
                        path=module_path,
                        content=command,
                    )
                    writer.add_document(
                        title=module_path,
                        path=module_path,
                        content=description,
                    )
        writer.commit()

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
    async def limokacmd(self, message):
        """[query] - Search module"""
        args = utils.get_args_raw(message)

        if len(args) <= 1:
            return await utils.answer(message, self.strings["?"])

        if not args:
            return await utils.answer(message, self.strings["noargs"])

        modules = self.modules

        await utils.answer(
            message,
            self.strings["wait"].format(
                count=len(modules),
                fact=random.choice(self.strings["facts"]),
                query=args,
            ),
        )

        searcher = Search(args.lower(), self.ix)
        try:
            result = searcher.search_module()
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

        logger.info(self.strings["found"])

        trusted_dev = False

        if '/'.join((str(module_path).split('/'))[:2]) in self.trusted["trusted"]:
            trusted_dev = True

        logger.info('/'.join((str(module_path).split('/'))[:2]))
        logger.info(self.trusted)

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
                    url=self.config["limoka_url"],
                    username=dev_username,
                    commands="".join(commands),
                    prefix=self.get_prefix(),
                    module_path=module_path.replace("\\", "/"),
                    tag=self.strings["tag_trust"] if trusted_dev else self.strings["tag_nontrust"]
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
                    url=self.config["limoka_url"],
                    username=dev_username,
                    commands="".join(commands),
                    prefix=self.get_prefix(),
                    module_path=module_path,
                    tag=self.strings["tag"] if trusted_dev else ""
                ),
            )

    @loader.inline_handler()
    async def limoka(self, query):
        """[query] - Inline search modules"""

        if not query.args:
            return {
                "title": "No query",
                "description": self.strings["inlinenoargs"],
                "thumb": "https://img.icons8.com/?size=100&id=NIWYFnJlcBfr&format=png&color=000000",
                "message": self.strings["inlinenoargs"],
            }

        modules = self.modules

        searcher = Search(query.args, self.ix)

        try:
            results = searcher.search_module(best_match=False)
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

        inline_results = []
        for path in results:
            module_info = modules.get(path)
            if module_info and module_info.get("commands"):
                inline_results.append({
                    "title": "{0}".format(utils.escape_html(module_info["name"])),
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
                        url=self.config["limoka_url"],
                        description=module_info["description"],
                        username=module_info["meta"].get("developer", "Unknown"),
                        commands="".join(self.generate_commands(module_info)),
                        module_path=path.replace("\\", "/"),
                        prefix=self.get_prefix(),
                    ),
                })

        return inline_results