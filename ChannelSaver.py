#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.functions.channels import ToggleSignaturesRequest
from telethon.tl.types import (
    Message,
    MessageMediaUnsupported,
    MessageMediaPoll,
    Channel,
    Chat,
    User
)
from telethon.tl.functions.account import UpdateProfileRequest
import asyncio
import io

class ChannelSaver(loader.Module):
    """猫ちゃん | Saves messages and media from private channels where it's forbidden"""

    strings = {
        "name": "ChannelSaver",
        "start": "<emoji document_id=5444965061749644170>👨‍💻</emoji> <i>It will take a few minutes.... probably much more</i>",
        "fwd": "forwarded from"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "your_channel",
                None,
                lambda: "Specify your channel ID",
                validator=loader.validators.TelegramID()
            ),
            loader.ConfigValue(
                "some_channel",
                None,
                lambda: "Specify some another channel ID",
                validator=loader.validators.TelegramID()
            )
        )

    async def checkData(self, iterList, item):
        is_poll = False
        is_ignore = False
        is_media = True if not (item.media is None) else False
        if is_media and (isinstance(item.media, (MessageMediaUnsupported, MessageMediaPoll)) or hasattr(item.media, "months")):
            is_ignore = True
        try:
            text = item.text
        except:
            text = "§"

        media = None
        if is_media and text == "":
            is_noneCaption = True
            media = io.BytesIO(await item.download_media(bytes))
            if isinstance(media, MessageMediaUnsupported):
                media = None
            elif is_ignore:
                pass
            elif hasattr(item.media, "photo"):
                media.name = "photo.png"
            else:
                media.name = item.media.document.mime_type.replace("/", ".")

        else:
            is_noneCaption = False

        is_fwd = True if not (item.fwd_from is None) else False
        if is_fwd:
            if not (item.fwd_from.from_id is None):
                name_id = item.fwd_from.from_id
                try:
                    entity = await self.client.get_entity(name_id)
                    if isinstance(entity, (Channel, Chat)):
                        name = entity.title

                    elif isinstance(entity, User):
                        if not (entity.first_name is None):
                            name = "".join((
                                entity.first_name,
                                (
                                    entity.last_name
                                    if not (entity.last_name is None) 
                                    else ""
                                )
                            ))
                        else:
                            name = "Deleted"

                except:
                    name = "Unknown"
                    name_id = None
            else:
                name = (
                    item.fwd_from.from_name
                    if not (item.fwd_from.from_name is None) 
                    else "Unknown"
                )
                name_id = None
                
        else:
            name = None
            name_id = None

        is_author = True if not(item.post_author is None) else False
        if is_author:
            author = item.post_author
        else:
            author = "."

        _dict = {
            "media": media,
            "text": text,
            "author": author,
            "name": name,
            "id": name_id,
            "is_media": is_media,
            "is_fwd": is_fwd,
            "is_noneCaption": is_noneCaption
        }
        iterList.append(_dict)
        return iterList


    async def psavecmd(self, message: Message):
        """ [limit: int] - save all the media and messages from specified channel"""
        args = (utils.get_args_raw(message)).split()
        limit = None
        if len(args) > 0:
            limit = int(args[0]) if args[0].isdigit() else None
        yourChannel = self.config["your_channel"]
        someChannel = self.config["some_channel"]
        if not all(isinstance(i, Channel) for i in [
            (await self.client.get_entity(yourChannel)),
            (await self.client.get_entity(someChannel))
        ]):
            await utils.answer(message, "<i>Please specify a channel ID</i>")
            return

        initName = (await self.client.get_entity(self.tg_id)).first_name
        iterList = []
        await utils.answer(message, self.strings["start"])
        try:
            await self.client(ToggleSignaturesRequest(yourChannel, enabled=True))
        except:
            pass

        async for i in self.client.iter_messages(someChannel, limit=limit):
            await self.checkData(iterList, item=i)

        iterList = iterList[::-1]
        for i in iterList:
            media = i["media"]
            text = i["text"]
            author = i["author"]
            name = i["name"]
            name_id = i["id"]
            is_media = i["is_media"]
            is_fwd = i["is_fwd"]
            is_noneCaption = i["is_noneCaption"]
            if not is_media and text == "§":
                continue

            if (await self.client.get_me()).first_name != author:
                await self.client(UpdateProfileRequest(first_name=author))
            if is_media and not (media is None):
                if is_noneCaption:
                    try:
                        await message.client.send_file(
                            yourChannel,
                            media
                        )
                    except:
                        await message.client.send_message(
                            yourChannel,
                            "<i>Just a poll</i>"
                        )
                    try:
                        await message.client.send_message(
                            yourChannel,
                            f"↑ <b>{self.strings['fwd']} <a href='tg://user?id={name_id}'>{name}</a></b>" if not (name_id is None) else f"<b>{self.strings['fwd']} {name}</b>" if not (name is None) else ""
                        )
                    except:
                        pass
                else:
                    await message.client.send_file(
                        yourChannel,
                        media,
                        caption="".join((
                            f"<b>{self.strings['fwd']} <a href='tg://user?id={name_id}'>{name}</a>:</b>\n\n" if not (name_id is None) else f"<b>{self.strings['fwd']} {name}:</b>\n\n" if not (name is None) else "",
                            text
                        ))
                    )
                await asyncio.sleep(20)
            else:
                await message.client.send_message(
                    yourChannel,
                    "".join((
                        f"<b>{self.strings['fwd']} <a href='tg://user?id={name_id}'>{name}</a>:</b>\n\n" if not (name_id is None) else f"<b>{self.strings['fwd']} {name}:</b>\n\n" if not (name is None) else "",
                        text
                    ))
                )
                await asyncio.sleep(20)
        await self.client(UpdateProfileRequest(first_name=initName))
        await utils.answer(message, "<emoji document_id=5233638613358486264>🚗</emoji> <b>Done</b>")
