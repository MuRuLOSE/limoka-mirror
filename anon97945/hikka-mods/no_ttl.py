__version__ = (0, 0, 2)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2025
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

import logging

from telethon.tl.types import Message, UpdateNewChannelMessage, MessageService
from telethon.tl.functions.messages import SetHistoryTTLRequest
from telethon.tl.functions.channels import GetFullChannelRequest


from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class NoTTLMod(loader.Module):
    """
    Send messages without TTL.
    """

    strings = {
        "name": "Apo-NoTTL",
        "developer": "@anon97945",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
        "_cmd_nottl": "Send a message without TTL. Can be used as a reply or with arguments.",
        "_cmd_cnottl": "Open the config for the module.",
        "no_args": "No args are given or not replied to a message...",
    }

    strings_en = {}

    strings_de = {
        "_cfg_cst_auto_migrate": "Ob Änderungen beim Start automatisch migriert werden sollen.",
        "_cmd_notll": "Senden Sie eine Nachricht ohne TTL. Kann als Antwort oder mit Argumenten verwendet werden.",
        "_cmd_cnottl": "Öffnen Sie die Konfiguration für das Modul.",
        "no_args": "Keine Argumente angegeben oder nicht auf eine Nachricht geantwortet...",

    }

    strings_ru = {
        "_cfg_cst_auto_migrate": "Автоматически мигрировать определенные изменения при запуске.",
        "_cmd_notll": "Отправить сообщение без TTL. Может использоваться в качестве ответа или с аргументами.",
        "_cmd_cnottl": "Открыть конфигурацию модуля.",
        "no_args": "ргументы не указаны или не ответили на сообщение...",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClas
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

    async def on_dlmod(self, client, _):
        return

    async def cnottlcmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def nottlcmd(self, message: Message):
        """
        Command to send a message without TTL.
        """
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message() if message.is_reply else None

        if not args and not reply:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_args", self.all_strings, message),
            )
            return

        chat_id = utils.get_chat_id(message)
        old_ttl = (await self.client(GetFullChannelRequest(chat_id))).full_chat.ttl_period

        ttl_msg_id = await self._set_ttl(chat_id, 0)

        await self.client.send_message(chat_id, reply if reply else args, reply_to=utils.get_topic(message))

        restore_ttl_msg_id = await self._set_ttl(chat_id, old_ttl)

        await self._client.delete_messages(chat_id, [ttl_msg_id, restore_ttl_msg_id, message.id])

    async def _set_ttl(self, chat_id: int, ttl: int) -> int:
        """
        Set the TTL for the chat and return the message ID of the TTL update.
        """
        ttl_req = await self.client(SetHistoryTTLRequest(chat_id, ttl))
        ttl_msg = next(
            (update for update in ttl_req.updates if isinstance(update, UpdateNewChannelMessage) and isinstance(update.message, MessageService)),
            None
        )
        return ttl_msg.message.id if ttl_msg else None
