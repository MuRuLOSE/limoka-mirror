#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import utils, loader
from telethon.tl.types import (
    Message,
    Chat,
    Channel,
    User
)
import asyncio

class Sender(loader.Module):
    """猫ちゃん | Massively sending message to some kind of chat"""

    strings = {
        "name": "Sender"
    }

    async def sendToPm(self, send_list):
        async for i in self.client.iter_dialogs():
            entity = await self.client.get_entity(i.id)
            if isinstance(entity, User):
                send_list.append(i.id)

    async def sendToGroup(self, send_list):
        async for i in self.client.iter_dialogs():
            entity = await self.client.get_entity(i.id)
            if isinstance(entity, Chat) or isinstance(entity, Channel) and getattr(entity, "broadcast") is False:
                send_list.append(i.id)
 
    async def sendToChannel(self, send_list):
        async for i in self.client.iter_dialogs():
            entity = await self.client.get_entity(i.id)
            if isinstance(entity, Channel) and getattr(entity, "broadcast") is True:
                send_list.append(i.id)

    async def sendToAll(self, send_list):
        async for i in self.client.iter_dialogs():
            send_list.append(i.id)


    async def sendcmd(self, message: Message):
        """ [pm / group / channel] <message> - start massive sending"""
        args = utils.get_args_raw(message)
        send_list = []
        err_count = 0
        text = args.split()[1] if args.split()[0] in ["pm", "group", "channel"] else args

        if not args:
            await utils.answer(message, "<i>Specify args</i>")
            return
 
        q = await utils.answer(message, "<i>Sending...</i>")

        if_var = args.split()[0]

        if if_var == "pm":
            await self.sendToPm(send_list)
        elif if_var == "group":
            await self.sendToGroup(send_list)
        elif if_var == "channel":
            await self.sendToChannel(send_list)
        else:
            await self.sendToAll(send_list)

        for i in send_list:
            try:
                await message.client.send_message(i, text)
                await asyncio.sleep(2)
            except:
                err_count += 1
                continue

        await utils.answer(q, f"<i>Message has been sent</i>\n\n<i>Couldn't send message to <u>{err_counter}</u> chats</i>")
        send_list = []
        err_count = 0