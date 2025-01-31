#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall
import asyncio

NAME = "Counter"

class Counter(loader.Module):
    """猫ちゃん | InlineCounter"""

    strings = {
        "name": "Counter",
        "count": "Counter: {}"
    }

    async def cresetcmd(self, message: Message):
        """ [-u] [-c] - reset counter\n-u (users list) -c (counts list)"""
        args = (utils.get_args_raw(message)).split()
        if all(i not in ["-u", "-c"] for i in args):
            await utils.answer(message, "<b>Incorrect flag</b>")
            await asyncio.sleep(4)
            await message.delete()
            return

        if "-u" in args:
            self.db.set(NAME, "u", [])
        if "-c" in args:
            self.db.set(NAME, "c", 0)
        await message.delete()
        return

    async def countcmd(self, message: Message):
        """ - creates an inline button for counting a presses"""
        if not self.db.get(NAME, "c"):
            self.db.set(NAME, "c", 0)

        if not self.db.get(NAME, "u"):
            self.db.set(NAME, "u", [])

        q = self.db.get(NAME, "c")

        await self.inline.form(
            text=self.strings["count"].format(q),
            message=message,
            reply_markup=[
                {
                    "text": "Click",
                    "callback": self.back
                }
            ],
            disable_security=True
        )


    async def back(self, call: InlineCall):
        id = call.from_user.id
        if id in self.db.get(NAME, "u"):
            return

        q = self.db.get(NAME, "c")
        q = q + 1
        self.db.set(NAME, "c", q)

        d = self.db.get(NAME, "u")
        d.append(id)
        self.db.set(NAME, "u", d)

        await call.edit(
            text=self.strings["count"].format(q),
            reply_markup=[
                {
                    "text": "Click",
                    "callback": self.back
                }
            ],
            disable_security=True
        )
