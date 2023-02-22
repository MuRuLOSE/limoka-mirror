#
#█▀█ █▀▀ █▄░█ █▀▀ █▀▀ █▀█ █ █▄░█
#█▀▀ ██▄ █░▀█ █▄█ █▄█ █▀▄ █ █░▀█
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @penggrin
# meta banner: https://raw.githubusercontent.com/darkmodules/assets/master/Irismanager.png
# scope: hikka_only

from .. import loader, utils
import logging

logger = logging.getLogger(__name__)


@loader.tds
class IrisManagerMod(loader.Module):
    """Iris Bot Wrapper"""

    strings = {
        "name": "IrisManager",
        "config_delete_cmds": "Delete the messages IrisManager sends?",
        "bot": "🤖 Bot",
        "user": "👨‍🦰 User",
        "me": "🐱 Me",
        "target": "🦊 Target",
        "cant_get_user_info": "🚫 Cant get information about that user!"
    }
    strings_ru = {
        "config_delete_cmds": "Удалять сообщения которые отправляет IrisManager?",
        "bot": "🤖 Бот",
        "user": "👨‍🦰 Юзер",
        "me": "🐱 Я",
        "target": "🦊 Цель",
        "cant_get_user_info": "🚫 Не могу получить информацию об этом пользователе!"
    }

    def list_to_str(self, a = None):
        if (a is None) or (len(a) < 1):
            return ""

        return ' '.join(str(b) for b in a)

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "delete_cmds",
                True,
                lambda: self.strings("config_delete_cmds"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self.client = client

    async def __iriscommand(self, command: str, message, force_reply = None, delete_result = True, use_args = True):
        reply = await message.get_reply_message() or force_reply
        if use_args:
            args = self.list_to_str(utils.get_args(message))
        else:
            args = ""
        if reply:
            result = await reply.reply(f"{command} {args}")
        else:
            result = await message.respond(f"{command} {args}")
        await message.delete()
        if delete_result and self.config["delete_cmds"]:
            await result.delete()
        #return result

    def get_id(self, target):
        return f"<b><i>{self.strings('bot') if target.bot else self.strings('user')}:</i></b>\n<code>{target.first_name}</code> {f'<code>{target.last_name}</code>' if target.last_name else ''}\n<code>{target.id}</code> {f'(<code>{target.username}</code>)' if target.username else ''}"

    @loader.command(ru_doc="[id:str OR int] - Возвращает данные о пользователе с помощью его айди / юзернейма, либо с помощью ответа")
    async def idcmd(self, message):
        """[id:str OR int] - Returns information about the user from their id / username, or with an reply"""
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        target = None

        try:
            if reply:
                target = await self.client.get_input_entity(reply.from_id)
                target = await self.client.get_entity(target)
            else:
                try:
                    target = await self.client.get_input_entity(int(args[0]))
                except:
                    target = await self.client.get_input_entity(args[0])
                target = await self.client.get_entity(target)

            await utils.answer(message, f'{self.strings("me")}:\n\n{self.get_id(await self.client.get_me())}\n\n\n{self.strings("target")}:\n\n{self.get_id(target)}')
        except Exception as e:
            logger.error(f"Cant get information about the user (called by 'id' command)\nError: {e}")
            await utils.answer(message, f"{self.strings('cant_get_user_info')}\n\n❓ {e}")

    async def idkcmd(self, message):
        """.дк [anything]"""
        await self.__iriscommand(".дк", message)

    async def imdkcmd(self, message):
        """.дк [anything]"""
        await self.__iriscommand(".мдк", message)

    async def itopcmd(self, message):
        """.топ"""
        await self.__iriscommand(".топ", message)

    async def itopacmd(self, message):
        """.топ [count:int] вся"""
        args = utils.get_args(message)
        await self.__iriscommand(f".топ {args[0] if len(args) > 0 else 10} вся", message, use_args = False)

    async def ipingcmd(self, message):
        """Пинг"""
        await self.__iriscommand(f"Пинг", message, use_args = False)

    async def ibotcmd(self, message):
        """Бот"""
        await self.__iriscommand(f"Бот", message, use_args = False)

    async def istatuscmd(self, message):
        """.актив ириса"""
        await self.__iriscommand(f".актив ириса", message, use_args = False)

    async def iadminscmd(self, message):
        """.админы"""
        await self.__iriscommand(f".админы", message, use_args = False)

    async def ifarmcmd(self, message):
        """ферма"""
        await self.__iriscommand(f"ферма", message, use_args = False)

    async def imeshokcmd(self, message):
        """мешок"""
        await self.__iriscommand(f"мешок", message, use_args = False)

    async def ipcmd(self, message):
        """+ [user]"""
        args = utils.get_args(message)
        last = await self.client.get_messages(message.peer_id, limit=2)
        await self.__iriscommand(f"+", message, force_reply = last[1], delete_result = True, use_args = False)

    async def imcmd(self, message):
        """- [user]"""
        args = utils.get_args(message)
        last = await self.client.get_messages(message.peer_id, limit=2)
        await self.__iriscommand(f"-", message, force_reply = last[1], delete_result = True, use_args = False)

    async def usemecmd(self, message):
        """[anything]"""
        args = utils.get_args(message)
        last = await self.client.get_messages(message.peer_id, limit=2)
        await self.__iriscommand("", message, force_reply = last[1])

    async def iwarncmd(self, message):
        """Варн <user> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Варн {args[0]}\n", message)

    async def iwarntcmd(self, message):
        """Варн <user> <time:int> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Варн {args[0]} {args[1]}\n", message)

    async def imutecmd(self, message):
        """Мут <user> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Мут {args[0]}\n", message)

    async def imutetcmd(self, message):
        """Мут <user> <time:int> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Мут {args[0]} {args[1]}\n", message)

    async def ibancmd(self, message):
        """Бан <user> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Бан 267 дней {args[0]}\n", message)

    async def ibantcmd(self, message):
        """Бан <user> <time:int> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Бан {args[0]} {args[1]}\n", message)

    async def ikickcmd(self, message):
        """Кик <user> [reason:str]"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Кик {args[0]}\n", message)

    async def ireasoncmd(self, message):
        """Причина <user>"""
        args = utils.get_args(message)
        await self.__iriscommand(f"Причина {args[0]}", message, use_args = False)

    async def dmcmd(self, message):
        """-смс"""
        args = utils.get_args(message)
        last = await self.client.get_messages(message.peer_id, limit=2)
        await self.__iriscommand(f"-смс", message, force_reply = last[1], delete_result = False, use_args = False)

        
