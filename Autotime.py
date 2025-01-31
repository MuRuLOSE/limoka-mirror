#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

import asyncio
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.utils import get_display_name
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Message

import re
import datetime
from .. import loader, utils

class Autotime(loader.Module):
    """猫ちゃん | Automatic stuff for your profile"""

    strings = {
        "name": "Autotime",
        "no_time": "You didn't specify a {time}",
        "cfg": "Positive or negative integer from -12 to 12"
    }

    def __init__(self):
        self.bio_on = False
        self.name_on = False
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "timezone",
                "0",
                lambda: self.strings['cfg'],
                validator=loader.validators.Integer()
            )
        )

    async def client_ready(self):
        self.me = await self.client.get_me()

    def _time(self):
        offset = datetime.timedelta(hours=self.config["timezone"])
        tz = datetime.timezone(offset)
        now = datetime.datetime.now(tz)
        time = now.strftime("%H:%M")
        return time


    async def cfgsetcmd(self, message: Message):
        """ <number> - to specify a timezone\nregarding to UTC+0"""
        tz = utils.get_args_raw(message)
        q = await self.invoke(
            "fconfig",
            f"{self.strings('name')} timezone {tz}",
            message.chat.id
        )
        await self.client.delete_messages(
            message.chat.id,
            [message, q]
        )

    async def autonamecmd(self, message: Message):
        """ <text> - autotime in nickname | {time} must be specified in the text\nWrite without argument to disable"""
        args = utils.get_args_raw(message)

        if not args:
            self.name_on = False
            regex = r"\d\d:\d\d"
            name = utils.escape_html(get_display_name(self.me))
            name = re.sub(regex, "", name)
            name.replace("  ", "")

            await self.client(UpdateProfileRequest(first_name=name))
            await message.delete()
            return

        if "{time}" not in args:
            await utils.answer(message, self.strings["no_time"])
            return

        self.name_on = True
        await message.delete()

        while self.name_on:
            text = args.replace("{time}", self._time())
            await self.client(UpdateProfileRequest(first_name=text))
            await asyncio.sleep(180)

    async def autobiocmd(self, message: Message):
        """ <text> - autotime in bio | {time} must be specified in the text\nWrite without argument to disable"""
        args = utils.get_args_raw(message)

        if not args:
            self.bio_on = False
            regex = r"\d\d:\d\d"
            bio = (await self.client(GetFullUserRequest(self.tg_id))).full_user.about
            bio = re.sub(regex, "", bio)
            bio.replace("  ", " ")

            await self.client(UpdateProfileRequest(about=bio))
            await message.delete()
            return

        if "{time}" not in args:
            await utils.answer(message, self.strings["no_time"])
            return

        self.bio_on = True
        await message.delete()

        while self.bio_on:
            text = args.replace("{time}", self._time())
            await self.client(UpdateProfileRequest(about=text))
            await asyncio.sleep(180)
		
