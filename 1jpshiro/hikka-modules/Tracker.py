#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.types import Message
from ..inline.types import InlineCall
import datetime
import time as t
import re

NAME = "Tracker"

class Tracker(loader.Module):
    """猫ちゃん | This module tracks the change history of an usernames and nicknames of the users you added to the track list"""

    strings = {
        "name": "Tracker",
        "enabled": "The tracker was successfully enabled",
        "disabled": "The tracker was successfully disabled",
        "no_user": "Seems this user doesn't exist, try another ID/Username",
        "change_status": "You just changed a status of tracking the user",
        "new_user": "You've successfully added a new user to track",
        "no_stat": "You're currently tracking no user",
        "only_one": "You're currently tracking only one user",
        "exists": "This user already exists in the track list, he's ID is {}",
        "cfg": "Specify a time-span for the cooldown before next check"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "cooldown",
                120,
                lambda: self.strings["cfg"],
                validator = loader.validators.Integer()
            )
        )

    async def client_ready(self, client, db):
        if not self.db.get(NAME, "status"):
            self.db.set(NAME, "status", False)
        if not self.db.get(NAME, "users"):
            self.db.set(NAME, "users", {})
        if not self.db.get(NAME, "time"):
            self.db.set(NAME, "time", t.time())

    async def showStat(self, call: InlineCall, ID, action) -> None:
        users = self.db.get(NAME, "users")
        if not users:
            await call.answer(self.strings["no_stat"])
            return

        user = await self.client.get_entity(users[str(ID)]["user_id"])

        ID = ID + 1 if action == "next" else ID - 1 if action == "previous" else ID
        if ID == 0:
            ID = len(users)
        elif ID > len(users):
            ID = 1

        ID = str(ID)
        if action == "change_status":
            users[ID]["active"] = not(users[ID]["active"])
            status = "In progress" if users[ID]["active"] else "Inactive"
            await call.answer(self.strings["change_status"])

        elif action == "previous":
            if len(users) == 1:
                await call.answer(self.strings["only_one"])
                return
            status = "In progress" if users[ID]["active"] else "Inactive"

        elif action == "next":
            if len(users) == 1:
                await call.answer(self.strings["only_one"])
                return
            status = "In progress" if users[ID]["active"] else "Inactive"

        self.db.set(NAME, "users", users)

        text = (
            f"<b>ID:</b> <a href='tg://user?id={user.id}'>{user.id}</a>\n"+
            "\n     <b>Nicknames</b>\n"+
            "\n".join(users[ID]["nicks"])+
            "\n\n     <b>Usernames</b>\n"+
            "\n".join(users[ID]["unames"])
        )

        await call.edit(
            text=text,
            reply_markup=[
                [
                    {
                        "text": f"Tracking status: {status}",
                        "callback": lambda call: self.showStat(call, int(ID), "change_status")
                    }
                ],
                [
                    {
                        "text": "Previous user",
                        "callback": lambda call: self.showStat(call, int(ID), "previous")
                    },
                    {
                        "text": "Next user",
                        "callback": lambda call: self.showStat(call, int(ID), "next")
                    }
                ]
            ]
        )

    @loader.command(ru_doc = " - включить / выключить слежку")
    async def trackcmd(self, message: Message):
        """ - enable / disable the tracking"""
        isEnDis = not(self.db.get(NAME, "status") is True)
        self.db.set(NAME, "status", isEnDis)

        if isEnDis is True:
            await utils.answer(message, self.strings["enabled"])

        elif isEnDis is False:
            await utils.answer(message, self.strings["enabled"])

    @loader.command(ru_doc = " <ID / Имя пользователя> - добавить нового пользователя в слежку")
    async def addtrackcmd(self, message: Message):
        """ <ID / Username> - add a new user to track"""
        args = utils.get_args_raw(message)
        users = self.db.get(NAME, "users")
        ID = len(users) + 1
        ID = str(ID)

        try:
            user = await self.client.get_entity(int(args) if args.isdigit() else args)

        except Exception:
            await utils.answer(message, self.strings["no_user"])
            return

        for _user in users:
            if users[_user]["user_id"] == user.id:
                await utils.answer(message, self.strings["exists"].format(_user))
                return

        UID = user.id
        nick = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        username = f"@{user.username}" if user.username else "<i>Empty</i>"

        time = datetime.datetime.now()
        date = str(time.date()).split('-')
        hms = str(time.time()).split(':')

        users[ID] = {
            "nicks": [
                "[{}.{}.{} - {}:{}:{}] {}".format(
                    date[2], date[1], date[0], hms[0], hms[1], hms[2].split('.')[0], nick
                )
            ],
            "unames": [
                "[{}.{}.{} - {}:{}:{}] {}".format(
                    date[2], date[1], date[0], hms[0], hms[1], hms[2].split('.')[0], username
                )
            ],
            "active": True,
            "user_id": UID
        }

        self.db.set(NAME, "users", users)
        await utils.answer(message, self.strings["new_user"])

    @loader.command(ru_doc = " - посмотреть статистику по пользователям")
    async def trackstatcmd(self, message: Message):
        """ - view the statistic about users you tracks"""
        users = self.db.get(NAME, "users")
        if not users:
            await utils.answer(message, self.strings["no_stat"])
            return

        ID = "1"
        user = await self.client.get_entity(users[ID]["user_id"])
        status = "In progress" if users[ID]["active"] else "Inactive"

        text = (
            f"<b>ID:</b> <a href='tg://user?id={user.id}'>{user.id}</a>\n"+
            "\n     <b>Nicknames</b>\n"+
            "\n".join(users[ID]["nicks"])+
            "\n\n     <b>Usernames</b>\n"+
            "\n".join(users[ID]["unames"])
        )

        await self.inline.form(
            text=text,
            message=message,
            reply_markup=[
                [
                    {
                        "text": f"Tracking status: {status}",
                        "callback": lambda call: self.showStat(call, int(ID), "change_status")
                    }
                ],
                [
                    {
                        "text": "Previous user",
                        "callback": lambda call: self.showStat(call, int(ID), "previous")
                    },
                    {
                        "text": "Next user",
                        "callback": lambda call: self.showStat(call, int(ID), "next")
                    }
                ]
            ]
        )

    async def watcher(self, message: Message):
        diff = t.time() - self.db.get(NAME, "time")
        if diff < self.config["cooldown"]:
            return

        users = self.db.get(NAME, "users")
        if not users:
            return

        for user in users:
            if users[user]["active"] is False:
                continue

            entity = await self.client.get_entity(users[user]["user_id"])
            nick = f"{entity.first_name} {entity.last_name}" if entity.last_name else entity.first_name
            username = f"@{entity.username}" if entity.username else "<i>Empty</i>"

            time = datetime.datetime.now()
            date = str(time.date()).split('-')
            hms = str(time.time()).split(':')

            if nick != re.sub(r"\[.*\]", "", users[user]["nicks"][-1]).strip():
                users[user]["nicks"].append(
                    "[{}.{}.{} - {}:{}:{}] {}".format(
                        date[2], date[1], date[0], hms[0], hms[1], hms[2].split('.')[0], nick
                    )
                )

            if username != re.sub(r"\[.*\]", "", users[user]["unames"][-1]).strip():
                users[user]["unames"].append(
                    "[{}.{}.{} - {}:{}:{}] {}".format(
                        date[2], date[1], date[0], hms[0], hms[1], hms[2].split(',')[0], username
                    )
                )

            self.db.set(NAME, "users", users)
            self.db.set(NAME, "time", t.time())