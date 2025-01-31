#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.types import Message
import asyncio

class DelMyMsgs(loader.Module):
    """猫ちゃん | Delete all your messages in current chat"""

    strings = {
        "name": "DelMyMsgs"
    }

    async def purgecmd(self, message: Message):
        """ [reply] [10s / 10m / 10h / 10d] - delete all your messages in current chat or only ones up to message you replyed to\nExample: 10h 3d"""
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
        async for i in self.client.iter_messages(message.chat.id):
            if i.from_id == self.tg_id:
                if reply:
                    if is_last:
                        break
                    if i.id == reply.id:
                        is_last = True
                await message.client.delete_messages(message.chat.id, [i.id])

        q = await utils.answer(message, "<b>Done</b>")
        await asyncio.sleep(2)
        await q.delete()