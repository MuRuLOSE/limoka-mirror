# ---------------------------------------------------------------------------------
# Author: @shiro_hikka
# Name: Message Eraser
# Description: Delete your messages in the current chat
# Commands: purge, stoppurge
# ---------------------------------------------------------------------------------
#              © Copyright 2025
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# ---------------------------------------------------------------------------------
# scope: hikka_only
# meta developer: @shiro_hikka
# meta banner: https://0x0.st/s/FIR0RnhUN5pZV5CZ6sNFEw/8KBz.jpg
# ---------------------------------------------------------------------------------

__version__ = (1, 1, 0)

from .. import loader, utils
from telethon.tl.types import Message
import asyncio

@loader.tds
class MessageEraser(loader.Module):
    """Delete your messages in the current chat"""

    strings = {
        "name": "MessageEraser",
        "enabled": "<emoji document_id=5289755247298747469>😒</emoji> It doesn't operates now anyway",
        "disabled": "<emoji document_id=5237870268541582966>❄️</emoji> Operation status changed to disabled"
    }

    async def client_ready(self):
        status = self.db.get(__name__, "status")
        if status is None:
            self.db.set(__name__, "status", False)


    async def stoppurgecmd(self, message: Message):
        """ Interupt the process of deletion"""
        status = self.db.get(__name__, "status")
        status = not status if status is True else status
        self.db.set(__name__, "status", status)

        if status is True:
            await utils.answer(message, self.strings["disabled"])
        else:
            await utils.answer(message, self.strings["enabled"])

    async def purgecmd(self, message: Message):
        """
        [reply] [10s / 10m / 10h / 10d] - delete all your messages in the current chat or only ones up to the message you replied to
        Posible to do in a specific time
        Example: 10h 3d
        """
        args = (utils.get_args_raw(message)).split()
        time = 0

        if args:
            for i in args:
                if len(i) < 2:
                    continue

                time += (
                    int(i[:-1]) if i[-1] == "s"
                    else int(i[:-1])*60 if i[-1] == "m"
                    else int(i[:-1])*3600 if i[-1] == "h"
                    else int(i[:-1])*86400 if i[-1] == "d"
                    else 0
                )

        reply = await message.get_reply_message()
        is_last = False

        await asyncio.sleep(time)
        self.db.set(__name__, "status", True)

        async for i in self.client.iter_messages(message.chat.id):
            if i.from_id == self.tg_id:
                if reply:
                    if is_last:
                        break
                    if i.id == reply.id:
                        is_last = True
                await message.client.delete_messages(message.chat.id, [i.id])

        await utils.answer(message, "<emoji document_id=5292186100004036291>🤩</emoji> Done")
