# meta developer: @limokanews

import aiohttp
import asyncio
import html
import json
import logging
import random
from typing import Dict, List, Optional, Tuple

from telethon.types import Message
from .. import loader, utils
from ..types import InlineQuery

logger = logging.getLogger("Limoka")


class LimokaAPI:
    """API client for fetching Limoka modules."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def initialize(self):
        """Initializes the aiohttp session."""
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Closes the aiohttp session."""
        if self.session:
            await self.session.close()

    async def get_all_modules(self) -> Dict:
        """Fetches all modules from the API.

        Returns:
            A dictionary containing module data, or an empty dictionary on failure.
        """
        url = f"{self.base_url}modules.json"
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                return json.loads(text)
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching modules from {url}: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from {url}: {e}, response: {text[:200] if 'text' in locals() else 'No response'}"
            )
            return {}


class Search:
    """Search class for module searching."""

    def __init__(self, query: str):
        self.query = query.lower()

    def search_module(self, contents: List[Dict]) -> List[str]:
        """Search for a module based on the query."""
        results = []
        for module in contents:
            if (
                module
                and "content" in module
                and module["content"]
                and self.query in module["content"].lower()
            ):
                results.append(module["id"])
        return results


class Limoka(loader.Module):
    """Hikka modules are now in one place with easy searching!"""

    strings = {
        "name": "Limoka",
        "wait": (
            "Just wait"
            "\n<emoji document_id=5404630946563515782>🔍</emoji> Searching {count} modules for: <code>{query}</code>"
            "\n<i>{fact}</i>"
        ),
        "found": (
            "<emoji document_id=5413334818047940135>🔍</emoji> Found module <b>{name}</b> for: <b>{query}</b>"
            "\n\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Description:</b> {description}"
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Developer:</b> {username}\n"
            "\n{commands}\n\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>"
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
        "not_found": "<emoji document_id=5210952531676504517>❌</emoji> No module found for: <i>{query}</i>",
        "no_args": "<emoji document_id=5210952531676504517>❌</emoji> Please provide a search query.",
        "short_query": "<emoji document_id=5951895176908640647>🔎</emoji> Query too short or not found.",
        "no_info": "No information",
        "facts": [
            "<emoji document_id=5472193350520021357>🛡</emoji> The Limoka catalog is carefully moderated!",
            "<emoji document_id=5940434198413184876>🚀</emoji> Limoka's performance allows for fast module searches!",
        ],
        "inline_not_found": "No modules found.",
        "inline_short_query": "Enter a search query.",
        "inline_no_args": "Please enter a query.",
        "?": "<emoji document_id=6324006154869867807>🤔</emoji> Please provide a search query.",
        "404": "<emoji document_id=5210952531676504517>❌</emoji> No module found for: <i>{query}</i>",
        "inlinenoargs": "<emoji document_id=5210952531676504517>❌</emoji> Please provide a search query.",
        "inline404": "<emoji document_id=5210952531676504517>❌</emoji> No module found for this query.",
        "inline?": "<emoji document_id=6324006154869867807>🤔</emoji> Something went wrong, please try again.",
    }

    strings_ru = {
        "wait": (
            "Подождите"
            "\n<emoji document_id=5404630946563515782>🔍</emoji> Ищем среди {count} модулей по запросу: <code>{query}</code>"
            "\n<i>{fact}</i>"
        ),
        "found": (
            "<emoji document_id=5413334818047940135>🔍</emoji> Найден модуль <b>{name}</b> по запросу: <b>{query}</b>"
            "\n\n<b><emoji document_id=5418376169055602355>ℹ️</emoji> Описание:</b> {description}"
            "\n<b><emoji document_id=5418299289141004396>🧑‍💻</emoji> Разработчик:</b> {username}\n"
            "\n{commands}\n\n<emoji document_id=5411143117711624172>🪄</emoji> <code>{prefix}dlm {url}{module_path}</code>"
        ),
        "command_template": "{emoji} <code>{prefix}{command}</code> {description}\n",
        "not_found": "<emoji document_id=5210952531676504517>❌</emoji> Модуль не найден по запросу: <i>{query}</i>",
        "no_args": "<emoji document_id=5210952531676504517>❌</emoji> Пожалуйста, введите запрос для поиска.",
        "short_query": "<emoji document_id=5951895176908640647>🔎</emoji> Слишком короткий запрос или ничего не найдено.",
        "no_info": "Нет информации",
        "facts": [
            "<emoji document_id=5472193350520021357>🛡</emoji> Каталог Limoka тщательно модерируется!",
            "<emoji document_id=5940434198413184876>🚀</emoji> Производительность Limoka обеспечивает быстрый поиск модулей!",
        ],
        "inline_not_found": "Модули не найдены.",
        "inline_short_query": "Введите поисковой запрос.",
        "inline_no_args": "Пожалуйста, введите запрос.",
        "?": "<emoji document_id=6324006154869867807>🤔</emoji> Пожалуйста, введите запрос для поиска.",
        "404": "<emoji document_id=5210952531676504517>❌</emoji> Модуль не найден по запросу: <i>{query}</i>",
        "inlinenoargs": "<emoji document_id=5210952531676504517>❌</emoji> Пожалуйста, введите запрос для поиска.",
        "inline404": "<emoji document_id=5210952531676504517>❌</emoji> Модуль не найден по этому запросу.",
        "inline?": "<emoji document_id=6324006154869867807>🤔</emoji> Что-то пошло не так, попробуйте еще раз.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "limoka_url",
                "https://git.vsecoder.dev/root/limoka/-/raw/main/",
                "Mirror: https://raw.githubusercontent.com/MuRuLOSE/limoka-mirror/refs/heads/main/",
                validator=loader.validators.String(),
            )
        )
        self.name = self.strings["name"]
        self._modules_cache: Dict = {}
        self._api: Optional[LimokaAPI] = None

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._api = LimokaAPI(self.config["limoka_url"])
        await self._api.initialize()
        asyncio.create_task(self._load_modules())

    async def _load_modules(self):
        """Loads modules data into the cache."""
        self._modules_cache = await self._api.get_all_modules()

    async def _get_modules(self) -> Dict:
        """Returns cached modules data, loading it if necessary.

        Returns:
            A dictionary containing module data.
        """
        if not self._modules_cache:
            await self._load_modules()
        return self._modules_cache

    def generate_commands(self, module_info: Dict) -> List[str]:
        """Generates formatted command strings for a module.

        Args:
            module_info: A dictionary containing module information.

        Returns:
            A list of formatted command strings.
        """
        commands = []
        command_count = 0
        for func in module_info.get("commands", []):
            for command, description in func.items():
                if command_count >= 9:
                    commands.append("...")
                    return commands
                command_count += 1
                emoji = self.strings["emojis"].get(command_count, "")
                commands.append(
                    self.strings["command_template"].format(
                        prefix=self.get_prefix(),
                        command=html.escape(command.replace("cmd", "")),
                        emoji=emoji,
                        description=html.escape(description or self.strings["no_info"]),
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

        modules = await self._get_modules()

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
            results = searcher.search_module(contents)
        except IndexError:
            return await utils.answer(message, self.strings["?"])

        if not results:
            return await utils.answer(message, self.strings["404"].format(query=args))

        module_path = results[0]

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
            try:
                translated_desc = await self._client.translate(
                    message.peer_id,
                    message,
                    to_lang=self._db.get("hikka.translations", "lang", "en")[0:2],
                    raw_text=description,
                    entities=message.entities,
                )
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
                translated_desc = description

        commands = self.generate_commands(module_info)

        module_path_for_dlm = module_path.replace("\\", "/")

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
                    module_path=module_path_for_dlm,
                ),
            )
        except Exception as e:
            logger.exception(f"Error sending module info: {e}")
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
                    module_path=module_path_for_dlm,
                ),
            )

    @loader.inline_handler()
    async def limoka(self, query: InlineQuery):
        """[query] - Inline search modules"""

        if not query.args:
            return await query.answer(
                [
                    {
                        "type": "article",
                        "id": "no_query",
                        "title": "No query",
                        "description": self.strings["inlinenoargs"],
                        "thumb_url": "https://img.icons8.com/?size=100&id=NIWYFnJlcBfr&format=png&color=000000",
                        "input_message_content": {
                            "message_text": self.strings["inlinenoargs"],
                            "parse_mode": "HTML",
                        },
                    }
                ]
            )

        modules = await self._get_modules()

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
            results = searcher.search_module(contents)
        except IndexError:
            return await query.answer(
                [
                    {
                        "type": "article",
                        "id": "error",
                        "title": "Something went wrong...",
                        "description": self.strings["inline?"],
                        "thumb_url": "https://img.icons8.com/?size=100&id=rUSWMuGVdxJj&format=png&color=000000",
                        "input_message_content": {
                            "message_text": self.strings["inline?"],
                            "parse_mode": "HTML",
                        },
                    }
                ]
            )

        if not results:
            return await query.answer(
                [
                    {
                        "type": "article",
                        "id": "no_results",
                        "title": "No results",
                        "description": self.strings["inline404"],
                        "thumb_url": "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000",
                        "input_message_content": {
                            "message_text": self.strings["inline404"],
                            "parse_mode": "HTML",
                        },
                    }
                ]
            )

        inline_results = []
        for path in results:
            module_info = modules.get(path)
            if not module_info:
                logger.warning(f"Module info not found for path: {path}")
                continue

            name = module_info.get("name", "Unknown")
            description = module_info.get("description", "No description")
            commands = self.generate_commands(module_info)
            module_path_for_dlm = path.replace("\\", "/")

            formatted_message = (
                self.strings["found"]
                .format(
                    name=name,
                    query=query.args,
                    url=self.config["limoka_url"],
                    description=description,
                    username=module_info["meta"].get("developer", "Unknown"),
                    commands="".join(commands),
                    module_path=module_path_for_dlm,
                    prefix=self.get_prefix(),
                )
                .replace("<emoji ", "")
            )

            inline_results.append(
                {
                    "type": "article",
                    "id": path,
                    "title": f"{utils.escape_html(name)}",
                    "description": utils.escape_html(description),
                    "thumb_url": module_info["meta"].get(
                        "pic",
                        "https://img.icons8.com/?size=100&id=olDsW0G3zz22&format=png&color=000000",
                    ),
                    "input_message_content": {
                        "message_text": formatted_message,
                        "parse_mode": "HTML",
                    },
                }
            )

        await query.answer(inline_results)
