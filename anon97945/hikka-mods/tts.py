__version__ = (0, 1, 93)


# ▄▀█ █▄ █ █▀█ █▄ █ █▀█ ▀▀█ █▀█ █ █ █▀
# █▀█ █ ▀█ █▄█ █ ▀█ ▀▀█   █ ▀▀█ ▀▀█ ▄█
#
#           © Copyright 2024
#
#        developed by @anon97945
#
#     https://t.me/apodiktum_modules
#      https://github.com/anon97945
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @apodiktum_modules
# meta banner: https://t.me/apodiktum_dumpster/11
# meta pic: https://t.me/apodiktum_dumpster/13

# scope: ffmpeg
# scope: hikka_only
# scope: hikka_min 1.3.3

# requires: gtts pydub soundfile pyrubberband numpy AudioSegment wave
# apt-requirements: libsndfile1 gcc ffmpeg rubberband-cli
# ⚠️ Execute:
# sudo libsndfile1 gcc ffmpeg rubberband-cli -y
# In order for this module to work properly

import io
import logging
import os
from subprocess import PIPE, Popen

import pyrubberband
import soundfile
from gtts import gTTS
from pydub import AudioSegment, effects
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


async def audionormalizer(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    rawsound = AudioSegment.from_file(bytes_io_file, "wav")
    normalizedsound = effects.normalize(rawsound)
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format="wav")
    bytes_io_file.name = f"{filename}.wav"
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, filename, file_ext


async def audiohandler(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    content = bytes_io_file.getvalue()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "pipe:",
        "-acodec",
        "pcm_s16le",
        "-f",
        "wav",
        "-ac",
        "1",
        "pipe:",
    ]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{filename}.wav"
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return (
        io.BytesIO(out),
        filename,
        file_ext if out.startswith(b"RIFF\xff\xff\xff") else None,
    )


async def makewaves(bytes_io_file: io.BytesIO, filename: str, file_ext: str) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    content = bytes_io_file.getvalue()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "pipe:",
        "-c:a",
        "libopus",
        "-f",
        "opus",
        "-ac",
        "2",
        "pipe:",
    ]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = f"{filename}.ogg"
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return io.BytesIO(out), filename, file_ext


def represents_speed(s: str) -> bool:
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


async def speedup(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    speed: float,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format="wav")
    bytes_io_file.seek(0)
    bytes_io_file.name = f"{filename}.wav"
    return bytes_io_file, filename, file_ext


@loader.tds
class ApodiktumTTSMod(loader.Module):
    strings = {
        "name": "Apo-TextToSpeech",
        "developer": "@anon97945",
        "_cfg_tts_lang": "Set your language code for the TTS here.",
        "_cfg_tts_speed": "Set the desired speech speed.",
        "needspeed": "You need to provide a speed value between 0.25 and 3.0.",
        "needvoice": "<b>[TTS]</b> This command needs a voicemessage.",
        "no_reply": "<b>[TTS]</b> You need to reply to a voicemessage.",
        "no_speed": "<b>[TTS]</b> Your input was an unsupported speed value.",
        "processing": "<b>[TTS]</b> Message is being processed ...",
        "tts_needs_text": "<b>[TTS]</b> I need text to convert to speech!",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_tts_lang": "Stellen Sie hier Ihren Sprachcode für TTS ein.",
        "_cfg_tts_speed": "Stellen Sie die gewünschte Sprechgeschwindigkeit ein.",
        "_cmd_doc_ctts": "Dadurch wird die Konfiguration für das Modul geöffnet.",
        "needspeed": (
            "Sie müssen einen Geschwindigkeitswert zwischen 0.25 und 3.0 angeben."
        ),
        "needvoice": "<b>[TTS]</b> Dieser Befehl benötigt eine Sprachnachricht.",
        "no_reply": "<b>[TTS]</b> Sie müssen auf eine Sprachnachricht antworten.",
        "no_speed": (
            "<b>[TTS]</b> Ihre Eingabe war ein nicht unterstützter"
            " Geschwindigkeitswert."
        ),
        "processing": "<b>[TTS]</b> Nachricht wird verarbeitet ...",
        "tts_needs_text": (
            "<b>[TTS]</b> Ich brauche Text, um ihn in Sprache umzuwandeln!"
        ),
    }

    strings_ru = {
        "_cfg_tts_lang": "Установите ваш код страны для TTS здесь.",
        "_cfg_tts_speed": "Установите желаемую скорость речи.",
        "_cmd_doc_ctts": "Это откроет конфиг для модуля.",
        "needspeed": "Вам нужно предоставить значение скорости между 0.25 и 3.0",
        "needvoice": "<b>[TTS]</b> Этой команде нужно голосовое сообщение.",
        "no_reply": "<b>[TTS]</b> Вам нужно сделать реплай на голосовое сообщение.",
        "no_speed": (
            "<b>[TTS]</b> Ваш ввод является неподдерживаемым значением скорости."
        ),
        "processing": "<b>[TTS]</b> Сообщение обрабатывается...",
        "tts_needs_text": "<b>[TTS]</b> Мне нужен текст для преобразования в речь!",
    }

    all_strings = {
        "strings": strings,
        "strings_en": strings,
        "strings_de": strings_de,
        "strings_ru": strings_ru,
    }

    changes = {
        "migration1": {
            "name": {
                "old": "Apo TextToSpeech",
                "new": "Apo-TextToSpeech",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "tts_lang",
                "en",
                doc=lambda: self.strings("_cfg_tts_lang"),
            ),
            loader.ConfigValue(
                "tts_speed",
                1,
                doc=lambda: self.strings("_cfg_tts_speed"),
                validator=loader.validators.Float(minimum=0.25, maximum=3),
            ),
            loader.ConfigValue(
                "auto_migrate",
                True,
                doc=lambda: self.strings("_cfg_cst_auto_migrate"),
                validator=loader.validators.Boolean(),
            ),  # for MigratorClass
        )

    async def client_ready(self):
        self.apo_lib = await self.import_lib(
            "git.vsecoder.dev/-/raw/main/libs/apodiktum_library.py",
            suspend_on_error=True,
        )
        await self.apo_lib.migrator.auto_migrate_handler(
            self.__class__.__name__,
            self.strings("name"),
            self.changes,
            self.config["auto_migrate"],
        )

    async def cttscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def ttscmd(self, message: Message):
        """Convert text to speech with Google APIs"""
        speed = self.config["tts_speed"]
        text = utils.get_args_raw(message)
        if not text:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                await utils.answer(
                    message,
                    self.apo_lib.utils.get_str(
                        "tts_needs_text", self.all_strings, message
                    ),
                )
                return
        msg = await utils.answer(
            message,
            self.apo_lib.utils.get_str("processing", self.all_strings, message),
        )
        tts = await utils.run_sync(gTTS, text, lang=self.config["tts_lang"])
        voice = io.BytesIO()
        await utils.run_sync(tts.write_to_fp, voice)
        voice.seek(0)
        voice.name = "voice.mp3"
        filename, file_ext = os.path.splitext(voice.name)
        voice, filename, file_ext = await audiohandler(voice, filename, file_ext)
        voice.seek(0)
        voice, filename, file_ext = await speedup(
            voice, filename, file_ext, float(speed)
        )
        voice.seek(0)
        voice, filename, file_ext = await audionormalizer(voice, filename, file_ext)
        voice.seek(0)
        voice, filename, file_ext = await makewaves(voice, filename, file_ext)
        voice.seek(0)
        voice.name = filename + file_ext
        await utils.answer(msg, voice, voice_note=True)
        if msg.out:
            await msg.delete()

    async def speedvccmd(self, message: Message):
        """Speed up voice by x"""
        speed = utils.get_args_raw(message)
        if not message.is_reply:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_reply", self.all_strings, message),
            )
            return
        replymsg = await message.get_reply_message()
        if not replymsg.voice:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("needvoice", self.all_strings, message),
            )
            return
        if len(speed) == 0:
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("needspeed", self.all_strings, message),
            )
            return
        if not represents_speed(speed):
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_speed", self.all_strings, message),
            )
            return
        msg = await utils.answer(
            message,
            self.apo_lib.utils.get_str("processing", self.all_strings, message),
        )
        ext = replymsg.file.ext
        voice = io.BytesIO()
        voice.name = replymsg.file.name
        await replymsg.client.download_file(replymsg, voice)
        voice.name = f"voice{ext}"
        filename, file_ext = os.path.splitext(voice.name)
        voice.seek(0)
        voice, filename, file_ext = await audiohandler(voice, filename, file_ext)
        voice.seek(0)
        voice, filename, file_ext = await speedup(
            voice, filename, file_ext, float(speed)
        )
        voice.seek(0)
        voice, filename, file_ext = await audionormalizer(voice, filename, file_ext)
        voice.seek(0)
        voice, filename, file_ext = await makewaves(voice, filename, file_ext)
        voice.seek(0)
        voice.name = filename + file_ext
        await utils.answer(msg, voice, voice_note=True)
        if msg.out:
            await msg.delete()
