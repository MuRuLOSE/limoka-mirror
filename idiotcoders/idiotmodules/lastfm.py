__version__ = (1, 0, 5)

# meta pic: https://static.whypodg.me/mods!lastfm.png
# meta banner: https://mods.whypodg.me/badges/lastfm.jpg
# meta developer: @idiotcoders
# scope: hikka_only
# scope: hikka_min 1.2.10
# requires: pylast

import asyncio
import contextlib
import functools
import logging
import pylast
import requests

from traceback import format_exc
from typing import Optional
from types import FunctionType
from io import BytesIO

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.types import Message

from .. import loader, utils


logger = logging.getLogger(__name__)


@loader.tds
class LastFMMod(loader.Module):
    """LastFM Now (based on SpotifyNow)"""

    strings = {
        "name": "LastFM",
        "_cfg_token": "Enter API token from your Last.fm account 🤫",
        "_cfg_secret": "Enter API secret from your Last.fm account 🤫",
        "_cfg_username": "Enter username from your Last.fm account 🤫",
        "_cfg_passwd": "Enter password from your Last.fm account 🤫",
        "_cfg_autobio": "Enter a template for auto-bio\nArguments: {author} — author of track, {track} — title of track",
        "error": "<emoji document_id=5312526098750252863>❌</emoji> <b>Error occurred. Make sure you are authorized and the track is playing!</b>\n\n<code>{error}</code>",
        "no_auth": "<emoji document_id=5312526098750252863>❌</emoji> <b>You are unauthorized!</b>",
        "nothing_playing": "<emoji document_id=5974411134936025665>❌</emoji> <b>Nothing is playing right now!</b>",
        "no_args": "<emoji document_id=5974411134936025665>❌</emoji> <b>Specify the args!</b>",
        "autobioe": "<emoji document_id=5197688912457245639>✅</emoji> <b>Last.fm bio enabled</b>",
        "autobiod": "<emoji document_id=5197688912457245639>✅</emoji> <b>Last.fm bio disabled</b>",
        "top": "<emoji document_id=5456498809875995940>🏆</emoji> <b>Your top-{count} the most listened tracks</b>:\n{top}",
        "nores": "<emoji document_id=5974411134936025665>❌</emoji> <b>No results!</b>",
        "now_playing": "<emoji document_id=5291772653567221434>🎧</emoji> {author} - {track}",
        "search": "<emoji document_id=5291772653567221434>🎧</emoji> {}"
    }

    strings_ru = {
        "name": "LastFM",
        "_cfg_token": "Укажи API токен от аккаунта Last.fm 🤫",
        "_cfg_secret": "Укажи API секрет от аккаунта Last.fm 🤫",
        "_cfg_username": "Укажи логин от аккаунта Last.fm 🤫",
        "_cfg_passwd": "Укажи пароль от аккаунта Last.fm 🤫",
        "_cfg_autobio": "Укажи шаблон автобио\nАргументы: {author} — автор, {track} — название трека",
        "_cls_doc": "LastFM Now (основан на SpotifyNow)",
        "error": "<emoji document_id=5312526098750252863>❌</emoji> <b>Произошла ошибка. Убедитесь, что Вы автворизованы и музыка играет!</b>\n\n<code>{error}</code>",
        "no_auth": "<emoji document_id=5312526098750252863>❌</emoji> <b>Вы не авторизованы!</b>",
        "nothing_playing": "<emoji document_id=5974411134936025665>❌</emoji> <b>Ничего сейчас не играет!</b>",
        "no_args": "<emoji document_id=5974411134936025665>❌</emoji> <b>Укажите аргументы!</b>",
        "autobioe": "<emoji document_id=5197688912457245639>✅</emoji> <b>Авто-био для Last.fm включено</b>",
        "autobiod": "<emoji document_id=5197688912457245639>✅</emoji> <b>Авто-био для Last.fm выключено</b>",
        "top": "<emoji document_id=5456498809875995940>🏆</emoji> <b>Ваш топ-{count} самых прослушиваемых треков</b>:\n{top}",
        "nores": "<emoji document_id=5974411134936025665>❌</emoji> <b>Результатов не найдено!</b>",
        "now_playing": "<emoji document_id=5291772653567221434>🎧</emoji> {author} - {track}",
        "search": "<emoji document_id=5291772653567221434>🎧</emoji> {}"
    }


    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "LastFmToken",
                None,
                lambda: self.strings["_cfg_token"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "LastFmSecret",
                None,
                lambda: self.strings["_cfg_secret"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "LastFmLogin",
                None,
                lambda: self.strings["_cfg_username"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "LastFmPassword",
                None,
                lambda: self.strings["_cfg_passwd"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "AutoBioTemplate",
                "🎧🎵 {author} - {track}",
                lambda: self.strings["_cfg_autobio"],
                validator=loader.validators.String(),
            ),
        )


    async def client_ready(self, client, db):
        self._premium = getattr(await client.get_me(), "premium", False)
        try:
            self._netw = pylast.LastFMNetwork(
                api_key=self.config['LastFmToken'],
                api_secret=self.config['LastFmSecret'],
                username=self.config['LastFmLogin'],
                password_hash=pylast.md5(self.config['LastFmPassword'])
            )
            self._user = self._netw.get_user(self.config['LastFmLogin'])
            self.set("auth", True)
        except Exception:
            self.set("auth", False)

        if self.get("autobio", False):
            self.autobio.start()

        self.musicdl = await self.import_lib(
            "git.vsecoder.dev/-/raw/main/libs/musicdl.py",
            suspend_on_error=True,
        )


    def error_handler(func) -> FunctionType:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception:
                logger.exception(format_exc())
                with contextlib.supperss(Exception):
                    await utils.answer(
                        args[1],
                        args[0].strings['error'].format(error=format_exc())
                    )

        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__

        return wrapped


    @loader.loop(interval=90)
    async def autobio(self):
        if not self.get('auth', False):
            return
        now = self._user.get_now_playing()
        if not now:
            return

        now = self._user.get_now_playing()
        bio = self.config["AutoBioTemplate"].format(
            author = str(now.artist),
            track = str(now.title)
        )

        try:
            await self._client(
                UpdateProfileRequest(about=bio[: 140 if self._premium else 70])
            )
        except FloodWaitError as e:
            logger.info(f"Sleeping {max(e.seconds, 60)} bc of floodwait")
            await asyncio.sleep(max(e.seconds, 60))
            return


    @error_handler
    @loader.command(
        ru_doc="<название> 👉 Поиск по трекам. Работает без авторизации",
        alias="lsch"
    )
    async def lsearchcmd(self, message: Message):
        "<name of track> 👉 Search for tracks. Works without authorization"
        name = utils.get_args_raw(message)
        if not name:
            await utils.answer(
                message,
                self.strings['no_args']
            )
            return

        await self._open_track(track=name, message=message)


    @error_handler
    @loader.command(
        ru_doc="[кол-во треков в топе] 👉 Получить топ самых прослушиваемых треков. Вы можете указать кол-во треков в топе (необязательно)"
    )
    async def ltopcmd(self, message: Message):
        "[count of tracks in top] 👉 Get the top most listened tracks. You can enter the count of tracks (optional)"
        args = utils.get_args(message)
        c, out = 5, ""
        if len(args) > 0 and args[0].isdigit():
            c = int(args[0])
        top = self._user.get_top_tracks(limit=c)
        emj = {'1': '<emoji document_id=5280735858926822987>🥇</emoji>', '2': '<emoji document_id=5283195573812340110>🥈</emoji>', '3': '<emoji document_id=5282750778409233531>🥉</emoji>'}
        for i in range(len(top)):
            out += f"{(str(i+1) + '.') if str(i+1) not in list(emj.keys()) else emj[str(i+1)]} <b>{top[i].item.artist}</b> - <i>{top[i].item.title}</i> — {top[i].weight}\n"
        await utils.answer(
            message,
            self.strings['top'].format(count=c, top=out)
        )


    @error_handler
    @loader.command(
        ru_doc="👉 Включить/выключить авто-био"
    )
    async def lbiocmd(self, message: Message):
        """👉 Toggle bio playback streaming"""
        current = self.get("autobio", False)
        new = not current
        self.set("autobio", new)
        await utils.answer(
            message,
            self.strings[f"autobio{'e' if new else 'd'}"]
        )

        if new:
            self.autobio.start()
        else:
            self.autobio.stop()


    @error_handler
    @loader.command(
        ru_doc="👉 Покажет проигрываемый сейчас трек"
    )
    async def lnowcmd(self, message: Message):
        """👉 Shows track, that playing right now"""
        now = self._user.get_now_playing()
        if now is None:
            await utils.answer(
                message,
                self.strings['nothing_playing']
            )
            return
        artists = str(now.artist).split(', ')
        track = {'name': str(now.title), 'artists': []}
        track['artists'].append({'name': i for i in artists})
        await self._open_track(
            track=track, message=message,
            override_text=self.strings['now_playing'].format(
                author=str(now.artist), track=str(now.title)
            )
        )


    async def _open_track(
        self,
        track,
        message: Message,
        override_text: str = None,
    ):
        if type(track) is dict:
            name = track.get("name")
            artists = [
                artist["name"] for artist in track.get("artists", []) if "name" in artist
            ]
            full_song_name = f"{name} - {', '.join(artists)}"
        else:
            name = ""
            artists = []
            full_song_name = str(track)

        music = await self.musicdl.dl(full_song_name, only_document=True)

        if not override_text:
            override_text = (
                f"<emoji document_id=5291772653567221434>🎧</emoji> <b>{', '.join(artists)}</b> - <i>{name}</i>"
                if artists else
                f"<emoji document_id=5291772653567221434>🎧</emoji> <b>{full_song_name}</b>"
            )

        try:
            await self._client.send_file(
                message.peer_id,
                music,
                caption=override_text
            )
        except:
            await utils.answer(
                message,
                "Some error!"
            )
            return

        if message.out:
            await message.delete()
