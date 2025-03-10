__version__ = (1, 0, 27)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: hikka_only
# scope: hikka_min 1.3.3

import asyncio
import contextlib
import logging

from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
skip_update = ["[do not install]", "[unstable]", "[test]"]


@loader.tds
class ApodiktumAutoUpdateMod(loader.Module):
    """
    Automatically update your Hikka Userbot
    """

    strings = {
        "name": "Apo-AutoUpdater",
        "developer": "@anon97945",
        "_cfg_auto_update": (
            "Whether the Hikka Userbot should automatically update or not."
        ),
        "_cfg_auto_update_delay": (
            "Choose a delay to wait to start the automatic update."
        ),
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cfg_update_msg_read": "Whether to mark the message as read or not.",
        "skip_old": "The update was skipped due to a newer update.",
        "skip_update": "The update was skipped due to {}.\n{}",
        "updating": (
            "Hikka Userbot will be automatically updated in {} seconds.\n\n"
            "Changelog:\n{}"
        ),
    }

    strings_de = {
        "_cfg_auto_update": (
            "Ob der Hikka Userbot automatisch aktualisieren soll oder nicht."
        ),
        "_cfg_auto_update_delay": (
            "Wählen Sie eine Wartezeit bis zum Start des automatischen Updates."
        ),
        "_cfg_update_msg_read": (
            "Ob die Nachricht als gelesen markiert werden soll oder nicht."
        ),
        "_cmd_doc_cautoupdate": (
            "Dadurch wird die Konfiguration für das Modul geöffnet."
        ),
        "skip_old": "Das Update wurde aufgrund eines neueren Updates übersprungen.",
        "skip_update": "Das Update wurde wegen {} übersprungen.\n{}",
        "updating": (
            "Hikka Userbot wird in {} Sekunden automatisch aktualisiert.\n\n"
            "Changelog:\n{}"
        ),
    }

    strings_ru = {
        "_cfg_auto_update": (
            "Должен ли Hikka UserBot обновляться автоматически или нет."
        ),
        "_cfg_auto_update_delay": "Выберите задержку для автоматического обновления.",
        "_cfg_update_msg_read": (
            "Отмечать ли сообщение с обновлением как прочитанное или нет."
        ),
        "skip_old": (
            "Обновление было пропущено в связи с появлением более новой версии."
        ),
        "skip_update": "Обновление было пропущено из-за {}.\n{}",
        "_cmd_doc_cautoupdate": "Открыть конфиг модуля.",
        "updating": (
            "Hikka будет автоматически обновлена через {} секунд.\n\n"
            "Список изменений:\n{}"
        ),
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo AutoUpdater",
                "new": "Apo-AutoUpdater",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_update",
                True,
                doc=lambda: self.strings("_cfg_auto_update"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "mark_read",
                True,
                doc=lambda: self.strings("_cfg_update_msg_read"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "update_delay",
                "600",
                doc=lambda: self.strings("_cfg_auto_update_delay"),
                validator=loader.validators.Integer(minimum=60),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "git.vsecoder.dev/-/raw/main/libs/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )
        asyncio.ensure_future(self._check_on_load())

    async def cautoupdatecmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    @staticmethod
    async def _buttonhandler(
        bmsg: Message,
        chatid: int,
        caption1: str,
        caption2: str,
        data_btn1: str,
        data_btn2: str,
    ) -> bool:
        fnd_btn1 = False
        fnd_btn2 = False
        bmsg = await bmsg.client.get_messages(chatid, ids=bmsg.id)
        buttons = bmsg.buttons
        if (
            caption1 in bmsg.message and caption2 in bmsg.message
        ) and bmsg.buttons is not None:
            for row in buttons:
                for button in row:
                    if data_btn1 in str(button.data):
                        fnd_btn1 = True
                    if data_btn2 in str(button.data):
                        fnd_btn2 = True
                    if fnd_btn1 and fnd_btn2:
                        return True
        return False

    async def _autoupdate(self, message: Message):
        if self.config["mark_read"]:
            await self._client.send_read_acknowledge(
                message.peer_id,
                clear_mentions=True,
            )

        self.apo_lib.utils.log(
            logging.INFO,
            __name__,
            self.strings("updating").format(
                self.config["update_delay"],
                "\n".join(self.apo_lib.utils.raw_text(message).splitlines()[5:]),
            ),
        )
        await asyncio.sleep(self.config["update_delay"])
        with contextlib.suppress(Exception):
            return await message.click(0)

    async def _check_skip(self, message: Message) -> bool:
        last_commit = self.apo_lib.utils.raw_text(message).splitlines()[5].lower()
        for x in skip_update:
            if x.lower() in last_commit and "revert" not in last_commit:
                self.apo_lib.utils.log(
                    logging.INFO,
                    __name__,
                    self.strings("skip_update").format(x, last_commit),
                )
                return True
        return False

    async def _check_on_load(self):
        if not self.config["auto_update"]:
            return

        async for message in self.client.iter_messages(
            entity=self.inline.bot_id, limit=5
        ):
            if (
                isinstance(message, Message)
                and message.sender_id == self.inline.bot_id
                and await self._buttonhandler(
                    message,
                    self.inline.bot_id,
                    "🌘",
                    "🔮",
                    "hikka_update",
                    "hikka_upd_ignore",
                )
            ):
                if await self._check_skip(message):
                    return
                with contextlib.suppress(Exception):
                    self._autoupdate_task.cancel()
                    self.apo_lib.utils.log(
                        logging.INFO, __name__, self.strings("skip_old")
                    )
                self._autoupdate_task = asyncio.ensure_future(self._autoupdate(message))

    @loader.watcher("in", "only_messages", "only_pm")
    async def watcher(self, message: Message):
        if (
            self.config["auto_update"]
            and utils.get_chat_id(message) == self.inline.bot_id
            and message.sender_id == self.inline.bot_id
            and await self._buttonhandler(
                message,
                self.inline.bot_id,
                "🌘",
                "🔮",
                "hikka_update",
                "hikka_upd_ignore",
            )
        ):
            if await self._check_skip(message):
                return
            with contextlib.suppress(Exception):
                self._autoupdate_task.cancel()
                self.apo_lib.utils.log(logging.INFO, __name__, self.strings("skip_old"))
            self._autoupdate_task = asyncio.ensure_future(self._autoupdate(message))
            return
