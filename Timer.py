#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.types import Message
import re
import asyncio

class Timer(loader.Module):
    """猫ちゃん | Timer"""

    strings = {
        "name": "Timer",
        "q": "<b>Current Timer for {}</b>\n<emoji document_id=5303396278179210513>👾</emoji> {} <b>left</b>"
    }

    async def parseArgs(self, message, args, parsed):
        for i in args:
            if i[-1] not in ["h", "m", "s"]:
                args.remove(i)

        for i in args:
            parsed[i[-1]] = int(re.sub(r"[^0-9]", "", i))
        return parsed

    async def timercmd(self, message: Message):
        """ [5h 5m 5s] - turn on the timer"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Specify time</b>")
            return

        hours = 0
        mins = 0
        secs = 0
        parsed = {
            "h": None,
            "m": None,
            "s": None
        }
        args = args.split()
        r = await self.parseArgs(message, args, parsed)
        if all(r[i] is None for i in parsed):
            await utils.answer(message, "<b>Time isn't specified</b>")
            return

        if r["h"]:
            hours = r["h"] * 3600
        if r["m"]:
            mins = r["m"] * 60
        if r["s"]:
            secs = r["s"]
        t = secs + mins + hours
        c = f"{hours}:{mins}:{secs}"
        pretime = "<i>{}:{}</i>"

        while t > -1:
            h = f"{t//3600}"
            m = f"{t%3600//60}"
            s = f"{t%3600%60}"
            if t > 59:
                q = self.strings["q"].format(c, pretime.format(h, m))
            else:
                q = self.strings["q"].format(c, pretime.format(h, f"{m}:{s}"))
            try:
                await utils.answer(message, q)
            except:
                pass
            t -= 1
            await asyncio.sleep(1)

        regex = r"\..*\<.*?\>.*"
        a = re.sub(regex, "\n<emoji document_id=5222108309795908493>✨</emoji> <b>Time's over</b>", q.replace("\n", "."))
        await utils.answer(message, a)
