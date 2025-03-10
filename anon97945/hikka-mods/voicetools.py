__version__ = (1, 0, 35)


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
# requires: numpy scipy noisereduce soundfile pyrubberband

import asyncio
import io
import logging
import os

import noisereduce as nr
import numpy as np
import pyrubberband
import scipy.io.wavfile as wavfile
import soundfile
from pydub import AudioSegment, effects
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


async def getchattype(message: Message) -> str:
    if message.is_group:
        return "supergroup" if message.is_channel else "smallgroup"

    if message.is_channel:
        return "channel"

    if message.is_private:
        return "private"


def represents_nr(nr_lvl: str) -> bool:
    try:
        float(nr_lvl)
        return 0.01 <= float(nr_lvl) <= 1
    except ValueError:
        return False


def represents_pitch(pitch_lvl: str) -> bool:
    try:
        float(pitch_lvl)
        return -18 <= float(pitch_lvl) <= 18
    except ValueError:
        return False


def represents_speed(s: str) -> bool:
    try:
        float(s)
        return 0.25 <= float(s) <= 3
    except ValueError:
        return False


def represents_gain(s: str) -> bool:
    try:
        float(s)
        return -10 <= float(s) <= 10
    except ValueError:
        return False


async def audiohandler(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    new_file_ext: str,
    channels: int,
    codec: str,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    out = filename + new_file_ext
    if file_ext != new_file_ext:
        new_fe_nodot = new_file_ext[1:]

        with open(filename + file_ext, "wb") as f:
            f.write(bytes_io_file.getbuffer())

        bytes_io_file.seek(0)

        sproc = await asyncio.create_subprocess_shell(
            f"ffmpeg -y -i {filename + file_ext} -c:a {codec} -f {new_fe_nodot} -ar"
            f" 48000 -b:a 320k -ac {channels} {out}",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await sproc.communicate()

        with open(out, "rb") as f:
            bytes_io_file = io.BytesIO(f.read())

        bytes_io_file.seek(0)
        _, new_file_ext = os.path.splitext(out)

    if os.path.exists(out):
        os.remove(out)

    if os.path.exists(filename + file_ext):
        os.remove(filename + file_ext)

    return bytes_io_file, filename, new_file_ext


async def audiopitcher(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    pitch_lvl: float,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    format_ext = file_ext[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_shift = pyrubberband.pitch_shift(y, sr, pitch_lvl)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_shift, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    return bytes_io_file, filename, file_ext


async def audiodenoiser(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    nr_lvl: float,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    rate, data = wavfile.read(bytes_io_file)
    reduced_noise = nr.reduce_noise(
        y=data,
        sr=rate,
        prop_decrease=nr_lvl,
        stationary=False,
    )
    wavfile.write(bytes_io_file, rate, reduced_noise)
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, filename, file_ext


async def audionormalizer(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    gain: float,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    format_ext = file_ext[1:]
    rawsound = AudioSegment.from_file(bytes_io_file, format_ext)
    normalizedsound = effects.normalize(rawsound)
    normalizedsound = normalizedsound + gain
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format=format_ext)
    bytes_io_file.name = filename + file_ext
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, filename, file_ext


async def audiospeedup(
    bytes_io_file: io.BytesIO,
    filename: str,
    file_ext: str,
    speed: float,
) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    format_ext = file_ext[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    return bytes_io_file, filename, file_ext


async def dalekvoice(bytes_io_file: io.BytesIO, filename: str, file_ext: str) -> tuple:
    bytes_io_file.seek(0)
    bytes_io_file.name = filename + file_ext
    format_ext = file_ext[1:]

    sound = AudioSegment.from_wav(bytes_io_file)
    sound = sound.set_channels(2)
    sound.export(bytes_io_file, format=format_ext)
    bytes_io_file.seek(0)
    VB = 0.2
    VL = 0.4
    H = 4
    LOOKUP_SAMPLES = 1024
    MOD_F = 50

    def diode_lookup(n_samples: int) -> np.ndarray:
        result = np.zeros((n_samples,))
        for i in range(n_samples):
            v = float(i - float(n_samples) / 2) / (n_samples / 2)
            v = abs(v)
            if v < VB:
                result[i] = 0
            elif VB < v <= VL:
                result[i] = H * ((v - VB) ** 2) / (2 * VL - 2 * VB)
            else:
                result[i] = H * v - H * VL + (H * (VL - VB) ** 2) / (2 * VL - 2 * VB)
        return result

    rate, data = wavfile.read(bytes_io_file)
    data = data[:, 1]
    scaler = np.max(np.abs(data))
    data = data.astype(np.float) / scaler
    n_samples = data.shape[0]
    d_lookup = diode_lookup(LOOKUP_SAMPLES)
    diode = Waveshaper(d_lookup)
    tone = np.arange(n_samples)
    tone = np.sin(2 * np.pi * tone * MOD_F / rate)
    tone = tone * 0.5
    tone2 = tone.copy()
    data2 = data.copy()
    tone = -tone + data2
    data = data + tone2
    data = diode.transform(data) + diode.transform(-data)
    tone = diode.transform(tone) + diode.transform(-tone)
    result = data - tone
    result /= np.max(np.abs(result))
    result *= scaler
    wavfile.write(bytes_io_file, rate, result.astype(np.int16))
    bytes_io_file.name = filename + file_ext
    filename, file_ext = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, filename, file_ext


class Waveshaper:
    def __init__(self, curve):
        self.curve = curve
        self.n_bins = self.curve.shape[0]

    def transform(self, samples: int) -> np.ndarray:
        # normalize to 0 < samples < 2
        max_val = np.max(np.abs(samples))
        if max_val >= 1.0:
            result = samples / np.max(np.abs(samples)) + 1.0
        else:
            result = samples + 1.0
        result = result * (self.n_bins - 1) / 2
        return self.curve[result.astype(np.int)]


@loader.tds
class ApodiktumVoiceToolsMod(loader.Module):
    """
    Change, pitch, enhance your Voice. Also includes optional automatic modes.
    """

    strings = {
        "name": "Apo-VoiceTools",
        "developer": "@anon97945",
        "_cfg_gain_lvl": "Set the desired volume gain level for auto normalize.",
        "_cfg_nr_lvl": "Set the desired noisereduction level.",
        "_cfg_pitch_lvl": "Set the desired pitch level for auto pitch.",
        "_cfg_speed_lvl": "Set the desired speed level for auto speed.",
        "audiodenoiser_txt": "<b>[VoiceTools] Background noise is being removed.</b>",
        "audiohandler_txt": "<b>[VoiceTools] Audio is being transcoded.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Audiovolume is being changed.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": (
            "<b>[VoiceTools]</b> Current AutoVoiceTools in this Chat are:\n\n{}"
        ),
        "dalek_start": "<b>[VoiceTools]</b> Auto DalekVoice activated.",
        "dalek_stopped": "<b>[VoiceTools]</b> Auto DalekVoice deactivated.",
        "dalekvoice_txt": "<b>[VoiceTools] Dalek Voice is being applied.</b>",
        "downloading": "<b>[VoiceTools] Message is being downloaded...</b>",
        "error_file": "<b>[VoiceTools]</b> No file in the reply detected.",
        "gain_start": "<b>[VoiceTools]</b> Auto VolumeGain activated.",
        "gain_stopped": "<b>[VoiceTools]</b> Auto VolumeGain deactivated.",
        "makewaves_txt": "<b>[VoiceTools] Speech waves are being applied.</b>",
        "no_nr": (
            "<b>[VoiceTools]</b> Your input was an unsupported noise reduction level."
        ),
        "no_pitch": "<b>[VoiceTools]</b> Your input was an unsupported pitch level.",
        "no_speed": "<b>[VoiceTools]</b> Your input was an unsupported speed level.",
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer activated.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deactivated.",
        "nr_level": "<b>[VoiceTools]</b> Noise reduction level set to {}.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer activated.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deactivated.",
        "pitch_level": "<b>[VoiceTools]</b> Pitch level set to {}.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch activated.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deactivated.",
        "pitch_txt": "<b>[VoiceTools] Pitch is being applied.</b>",
        "speed_start": "<b>[VoiceTools]</b> Auto VoiceSpeed activated.",
        "speed_stopped": "<b>[VoiceTools]</b> Auto VoiceSpeed deactivated.",
        "speed_txt": "<b>[VoiceTools] Speed is being applied.</b>",
        "uploading": "<b>[VoiceTools] File is uploading.</b>",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice activated.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deactivated.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deactivated.",
        "_cfg_cst_auto_migrate": "Wheather to auto migrate defined changes on startup.",
    }

    strings_en = {}

    strings_de = {
        "_cfg_gain_lvl": (
            "Stellen Sie den gewünschten Lautstärkepegel für die automatische"
            " Normalisierung ein."
        ),
        "_cfg_nr_lvl": "Stellen Sie den gewünschten Rauschunterdrückungspegel ein.",
        "_cfg_pitch_lvl": (
            "Stellen Sie den gewünschten Tonhöhenpegel für die automatische"
            " Tonhöheneinstellung ein."
        ),
        "_cfg_speed_lvl": (
            "Stellen Sie die gewünschte Geschwindigkeitsstufe für die"
            " automatische Geschwindigkeit ein."
        ),
        "_cmd_doc_cvoicetoolscmd": (
            "Dadurch wird die Konfiguration für das Modul geöffnet."
        ),
        "audiodenoiser_txt": (
            "<b>[VoiceTools] Die Hintergrundgeräusche werden entfernt.</b>"
        ),
        "audiohandler_txt": "<b>[VoiceTools] Der Ton wird transkodiert.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Das Audiovolumen wird angepasst.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": (
            "<b>[VoiceTools]</b> Aktuelle AutoVoiceTools in diesem Chat sind:\n\n{}"
        ),
        "dalek_start": "<b>[VoiceTools]</b> Auto DalekVoice aktiviert.",
        "dalek_stopped": "<b>[VoiceTools]</b> Auto DalekVoice ist deaktiviert.",
        "dalekvoice_txt": "<b>[VoiceTools] Die Dalek-Stimme wird angewendet.</b>",
        "downloading": "<b>[VoiceTools] Die Nachricht wird heruntergeladen...</b>",
        "error_file": "<b>[VoiceTools]</b> Keine Datei in der Antwort gefunden.",
        "gain_start": "<b>[VoiceTools]</b> Auto VolumeGain aktiviert.",
        "gain_stopped": "<b>[VoiceTools]</b> Auto VolumeGain deaktiviert.",
        "makewaves_txt": "<b>[VoiceTools] Es werden Sprachwellen erstellt.</b>",
        "no_nr": (
            "<b>[VoiceTools]</b> Ihre Eingabe war ein nicht unterstützter"
            " Rauschunterdrückungspegel."
        ),
        "no_pitch": (
            "<b>[VoiceTools]</b> Ihre Eingabe war ein nicht unterstützter"
            " Tonhöhenpegel."
        ),
        "no_speed": (
            "<b>[VoiceTools]</b> Ihre Eingabe war eine nicht unterstützte"
            " Geschwindigkeitswert."
        ),
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer aktiviert.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deaktiviert.",
        "nr_level": "<b>[VoiceTools]</b> Rauschunterdrückungspegel auf {} eingestellt.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer aktiviert.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deaktiviert.",
        "pitch_level": "<b>[VoiceTools]</b> Die Tonhöhe ist auf {} eingestellt.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch aktiviert.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deaktiviert.",
        "pitch_txt": "<b>[VoiceTools] Pitch wird angewandt.</b>",
        "speed_start": "<b>[VoiceTools]</b> Auto VoiceSpeed aktiviert.",
        "speed_stopped": "<b>[VoiceTools]</b> Auto VoiceSpeed deaktiviert.",
        "speed_txt": "<b>[VoiceTools] Geschwindigkeit wird angewendet.</b>",
        "uploading": "<b>[VoiceTools] Datei wird hochgeladen.</b>",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice aktiviert.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deaktiviert.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deaktiviert.",
    }

    strings_ru = {
        "_cfg_gain_lvl": (
            "Установите желаемый уровень усиления громкости для автоматического"
            " питча. (Высоты тона)"
        ),
        "_cfg_nr_lvl": "Установите желаемый уровень шумоподавления.",
        "_cfg_pitch_lvl": "Установите желаемый уровень высоты тона для автонастройки.",
        "_cfg_speed_lvl": (
            "Установите желаемый уровень скорости для автоматической скорости."
        ),
        "_cmd_doc_cvoicetoolscmd": "Это откроет конфиг для модуля.",
        "audiodenoiser_txt": "<b>[VoiceTools] Фоновый шум удаляется.</b>",
        "audiohandler_txt": "<b>[VoiceTools] Аудио перекодируется.</b>",
        "audiovolume_txt": "<b>[VoiceTools] Аудиогромкость изменяется.</b>",
        "auto_anon_off": "<b>❌ Anon Voice.</b>",
        "auto_anon_on": "<b>✅ Anon Voice.</b>",
        "auto_dalek_off": "<b>❌ Dalek Voice.</b>",
        "auto_dalek_on": "<b>✅ Dalek Voice.</b>",
        "auto_gain_off": "<b>❌ Volumegain.</b>",
        "auto_gain_on": "<b>✅ Volumegain.</b>",
        "auto_norm_off": "<b>❌ Normalize.</b>",
        "auto_norm_on": "<b>✅ Normalize.</b>",
        "auto_nr_off": "<b>❌ NoiseReduction.</b>",
        "auto_nr_on": "<b>✅ NoiseReduction.</b>",
        "auto_pitch_off": "<b>❌ Pitching.</b>",
        "auto_pitch_on": "<b>✅ Pitching.</b>",
        "auto_speed_off": "<b>❌ Speed.</b>",
        "auto_speed_on": "<b>✅ Speed.</b>",
        "current_auto": (
            "<b>[VoiceTools]</b> Текущие авто-инструменты для работы с голосом"
            " в этом чате:\n\n{}"
        ),
        "dalek_start": "<b>[VoiceTools]</b> Активирован автоматический голос «Далека».",
        "dalek_stopped": (
            "<b>[VoiceTools]</b> Деактивирован автоматический голос «Далека»."
        ),
        "dalekvoice_txt": "<b>[VoiceTools] Голос «Далека» применяется.</b>",
        "downloading": "<b>[VoiceTools] Сообщение загружается...</b>",
        "error_file": "<b>[VoiceTools]</b> Не обнаружен файл в реплае.",
        "gain_start": (
            "<b>[VoiceTools]</b> Активировано автоматическое усиление громкости."
        ),
        "gain_stopped": (
            "<b>[VoiceTools]</b> Деактивировано автоматическое усиление громкости."
        ),
        "makewaves_txt": "<b>[VoiceTools] Речевые волны применяются.</b>",
        "no_nr": (
            "<b>[VoiceTools]</b> Введенное значение не является поддерживаемым уровнем"
            " шумоподавления."
        ),
        "no_pitch": (
            "<b>[VoiceTools]</b> Введенное значение не является поддерживаемым уровнем"
            " высоты тона."
        ),
        "no_speed": (
            "<b>[VoiceTools]</b> Введенное значение не является поддерживаемым уровнем"
            " скорости звука."
        ),
        "norm_start": "<b>[VoiceTools]</b> Активирована автонормализация голоса.",
        "norm_stopped": "<b>[VoiceTools]</b> Деактивирована автонормализация голоса.",
        "nr_level": "<b>[VoiceTools]</b> Уровень шумоподавления установлен на {}.",
        "nr_start": "<b>[VoiceTools]</b> Активировано автоматическое усиление голоса.",
        "nr_stopped": (
            "<b>[VoiceTools]</b> Деактивировано автоматическое усиление голоса."
        ),
        "pitch_level": "<b>[VoiceTools]</b> Уровень высоты тона установлен на {}.",
        "pitch_start": "<b>[VoiceTools]</b> Активирован авто-питч. (Высота тона)",
        "pitch_stopped": "<b>[VoiceTools]</b> Деактивирован авто-питч. (Высота тона)",
        "pitch_txt": "<b>[VoiceTools] Высота тона применяется.</b>",
        "speed_start": "<b>[VoiceTools]</b> Активировано автоускорение голоса.",
        "speed_stopped": "<b>[VoiceTools]</b> Деактивировано автоускорение голоса.",
        "speed_txt": "<b>[VoiceTools] Скорость применяется.</b>",
        "uploading": "<b>[VoiceTools] Файл загружается.</b>",
        "vcanon_start": (
            "<b>[VoiceTools]</b> Активирован автоматический «анонимный голос»"
        ),
        "vcanon_stopped": (
            "<b>[VoiceTools]</b> Деактивирован автоматический «анонимный голос»"
        ),
        "vtauto_stopped": (
            "<b>[VoiceTools]</b> Деактивированы все автоматические инструменты"
            " для работы с голосом."
        ),
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
                "old": "Apo Voicetools",
                "new": "Apo-Voicetools",
            },
        },
    }

    def __init__(self):
        self._ratelimit = []
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "pitch_lvl",
                "4",
                doc=lambda: self.strings("_cfg_pitch_lvl"),
                validator=loader.validators.Float(minimum=-18, maximum=18),
            ),
            loader.ConfigValue(
                "nr_lvl",
                "0.85",
                doc=lambda: self.strings("_cfg_nr_lvl"),
                validator=loader.validators.Float(minimum=0.01, maximum=1),
            ),
            loader.ConfigValue(
                "gain_lvl",
                "1.5",
                doc=lambda: self.strings("_cfg_gain_lvl"),
                validator=loader.validators.Float(minimum=-10, maximum=10),
            ),
            loader.ConfigValue(
                "speed_lvl",
                "1",
                doc=lambda: self.strings("_cfg_speed_lvl"),
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
        self._classname = self.__class__.__name__
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

    async def cvoicetoolscmd(self, message: Message):
        """
        This will open the config for the module.
        """
        name = self.strings("name")
        await self.allmodules.commands["config"](
            await utils.answer(message, f"{self.get_prefix()}config {name}")
        )

    async def vtdalekcmd(self, message):
        """reply to a file to change the voice"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        nr_lvl = self.config["nr_lvl"]
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".wav", "1", "pcm_s16le"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiodenoiser_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiodenoiser(file, filename, file_ext, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("dalekvoice_txt", self.all_strings, message),
        )
        file, filename, file_ext = await dalekvoice(file, filename, file_ext)
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtanoncmd(self, message):
        """reply to a file to change the voice into anonymous"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = io.BytesIO()
        file.name = replymsg.file.name
        nr_lvl = 0.8
        pitch_lvl = -4.5
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".wav", "1", "pcm_s16le"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiodenoiser_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiodenoiser(file, filename, file_ext, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("dalekvoice_txt", self.all_strings, message),
        )
        file, filename, file_ext = await dalekvoice(file, filename, file_ext)
        file.seek(0)
        file, filename, file_ext = await audiopitcher(
            file, filename, file_ext, pitch_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtpitchcmd(self, message):
        """reply to a file to pitch voice
        - Example: .vtpitch 12
          Possible values between -18 and 18"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        pitch_lvl = utils.get_args_raw(message)
        if not represents_pitch(pitch_lvl):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_pitch", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".flac", "1", "flac"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("pitch_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiopitcher(
            file, filename, file_ext, float(pitch_lvl)
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtspeedcmd(self, message):
        """reply to a file to increase speed and reduce length
        - Example: .vtspeed 1.5
          Possible values between 0.25 - 3"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        speed_lvl = utils.get_args_raw(message)
        if not represents_speed(speed_lvl):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_speed", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".flac", "1", "flac"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("speed_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiospeedup(
            file, filename, file_ext, float(speed_lvl)
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtgaincmd(self, message):
        """reply to a file to change the volume
        - Example: .vtgain 1
          Possible values between -10 - 10"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        gain_lvl = utils.get_args_raw(message)
        if not represents_gain(gain_lvl):
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("no_speed", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".flac", "1", "flac"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtenhcmd(self, message):
        """reply to a file to enhance voice quality with
        - Volume normalize
        - Background NoiseReduce (set your noisereduce level before)"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        nr_lvl = self.config["nr_lvl"]
        gain_lvl = 0
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".wav", "1", "pcm_s16le"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiodenoiser_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiodenoiser(file, filename, file_ext, nr_lvl)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtnormcmd(self, message):
        """reply to a file to normalize volume"""
        chatid = utils.get_chat_id(message)
        SendAsVoice = False
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        SendAsVoice = bool(replymsg.voice)
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        gain_lvl = 0
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".wav", "1", "pcm_s16le"
        )
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiovolume_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audionormalizer(
            file, filename, file_ext, gain_lvl
        )
        file.seek(0)
        if SendAsVoice:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ".ogg", "2", "libopus"
            )
        else:
            inline_msg = await utils.answer(
                inline_msg,
                self.apo_lib.utils.get_str(
                    "audiohandler_txt", self.all_strings, message
                ),
            )
            file, filename, file_ext = await audiohandler(
                file, filename, file_ext, ext, "1", "libmp3lame"
            )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=SendAsVoice)
        await inline_msg.delete()

    async def vtmp3cmd(self, message: Message):
        """reply to a file to convert it to mp3"""
        chatid = utils.get_chat_id(message)
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("audiohandler_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=False)
        await inline_msg.delete()

    async def vtspeechcmd(self, message):
        """reply to a file to convert it to speech"""
        chatid = utils.get_chat_id(message)
        if not message.is_reply:
            return
        replymsg = await message.get_reply_message()
        if not replymsg.media:
            return await utils.answer(
                message,
                self.apo_lib.utils.get_str("error_file", self.all_strings, message),
            )
        filename = replymsg.file.name or "voice"
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file = io.BytesIO()
        file.name = replymsg.file.name
        inline_msg = await self.inline.form(
            message=message,
            text=self.apo_lib.utils.get_str("downloading", self.all_strings, message),
            reply_markup={"text": "\u0020\u2800", "callback": "empty"},
        )
        await self._client.download_file(replymsg, file)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("makewaves_txt", self.all_strings, message),
        )
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".ogg", "2", "libopus"
        )
        file.seek(0)
        file.name = filename + file_ext
        inline_msg = await utils.answer(
            inline_msg,
            self.apo_lib.utils.get_str("uploading", self.all_strings, message),
        )
        await self._client.send_file(chatid, file, voice_note=True)
        await inline_msg.delete()

    async def vtautodalekcmd(self, message):
        """Turns on AutoDalekVoice for your own Voicemessages in the chat"""
        dalek_chats = self._db.get(self._classname, "dalek_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in dalek_chats:
            dalek_chats.append(chatid_str)
            self._db.set(self._classname, "dalek_watcher", dalek_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("dalek_start", self.all_strings, message),
            )
        else:
            dalek_chats.remove(chatid_str)
            self._db.set(self._classname, "dalek_watcher", dalek_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("dalek_stopped", self.all_strings, message),
            )

    async def vtautoanoncmd(self, message):
        """Turns on AutoAnonVoice for your own Voicemessages in the chat"""
        vcanon_chats = self._db.get(self._classname, "vcanon_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in vcanon_chats:
            vcanon_chats.append(chatid_str)
            self._db.set(self._classname, "vcanon_watcher", vcanon_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("vcanon_start", self.all_strings, message),
            )
        else:
            vcanon_chats.remove(chatid_str)
            self._db.set(self._classname, "vcanon_watcher", vcanon_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("vcanon_stopped", self.all_strings, message),
            )

    async def vtautonrcmd(self, message):
        """Turns on AutoNoiseReduce for your own Voicemessages in the chat"""
        nr_chats = self._db.get(self._classname, "nr_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in nr_chats:
            nr_chats.append(chatid_str)
            self._db.set(self._classname, "nr_watcher", nr_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("nr_start", self.all_strings, message),
            )
        else:
            nr_chats.remove(chatid_str)
            self._db.set(self._classname, "nr_watcher", nr_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("nr_stopped", self.all_strings, message),
            )

    async def vtautonormcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        norm_chats = self._db.get(self._classname, "norm_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in norm_chats:
            norm_chats.append(chatid_str)
            self._db.set(self._classname, "norm_watcher", norm_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("norm_start", self.all_strings, message),
            )
        else:
            norm_chats.remove(chatid_str)
            self._db.set(self._classname, "norm_watcher", norm_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("norm_stopped", self.all_strings, message),
            )

    async def vtautospeedcmd(self, message):
        """Turns on AutoSpeed for your own Voicemessages in the chat"""
        speed_chats = self._db.get(self._classname, "speed_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in speed_chats:
            speed_chats.append(chatid_str)
            self._db.set(self._classname, "speed_watcher", speed_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("speed_start", self.all_strings, message),
            )
        else:
            speed_chats.remove(chatid_str)
            self._db.set(self._classname, "speed_watcher", speed_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("speed_stopped", self.all_strings, message),
            )

    async def vtautopitchcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        pitch_chats = self._db.get(self._classname, "pitch_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in pitch_chats:
            pitch_chats.append(chatid_str)
            self._db.set(self._classname, "pitch_watcher", pitch_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("pitch_start", self.all_strings, message),
            )
        else:
            pitch_chats.remove(chatid_str)
            self._db.set(self._classname, "pitch_watcher", pitch_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("pitch_stopped", self.all_strings, message),
            )

    async def vtautogaincmd(self, message):
        """Turns on AutoVolumeGain for your own Voicemessages in the chat"""
        gain_chats = self._db.get(self._classname, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str not in gain_chats:
            gain_chats.append(chatid_str)
            self._db.set(self._classname, "gain_watcher", gain_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("gain_start", self.all_strings, message),
            )
        else:
            gain_chats.remove(chatid_str)
            self._db.set(self._classname, "gain_watcher", gain_chats)
            await utils.answer(
                message,
                self.apo_lib.utils.get_str("gain_stopped", self.all_strings, message),
            )

    async def vtautocmd(self, message):
        """Displays all enabled AutoVoice settings in the chat"""
        current = ""
        norm_chats = self._db.get(self._classname, "norm_watcher", [])
        nr_chats = self._db.get(self._classname, "nr_watcher", [])
        dalek_chats = self._db.get(self._classname, "dalek_watcher", [])
        pitch_chats = self._db.get(self._classname, "pitch_watcher", [])
        vcanon_chats = self._db.get(self._classname, "vcanon_watcher", [])
        speed_chats = self._db.get(self._classname, "speed_watcher", [])
        gain_chats = self._db.get(self._classname, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str in vcanon_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_anon_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_anon_off", self.all_strings, message)
                + "\n"
            )
        if chatid_str in dalek_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_dalek_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str(
                    "auto_dalek_off", self.all_strings, message
                )
                + "\n"
            )
        if chatid_str in pitch_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_pitch_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str(
                    "auto_pitch_off", self.all_strings, message
                )
                + "\n"
            )
        if chatid_str in speed_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_speed_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str(
                    "auto_speed_off", self.all_strings, message
                )
                + "\n"
            )
        if chatid_str in norm_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_norm_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_norm_off", self.all_strings, message)
                + "\n"
            )
        if chatid_str in gain_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_gain_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_gain_off", self.all_strings, message)
                + "\n"
            )
        if chatid_str in nr_chats:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_nr_on", self.all_strings, message)
                + "\n"
            )
        else:
            current = (
                current
                + self.apo_lib.utils.get_str("auto_nr_off", self.all_strings, message)
                + "\n"
            )
        return await utils.answer(
            message,
            self.apo_lib.utils.get_str(
                "current_auto", self.all_strings, message
            ).format(current),
        )

    async def vtautostopcmd(self, message):
        """Turns off AutoVoice for your own Voicemessages in the chat"""
        norm_chats = self._db.get(self._classname, "norm_watcher", [])
        nr_chats = self._db.get(self._classname, "nr_watcher", [])
        dalek_chats = self._db.get(self._classname, "dalek_watcher", [])
        pitch_chats = self._db.get(self._classname, "pitch_watcher", [])
        vcanon_chats = self._db.get(self._classname, "vcanon_watcher", [])
        speed_chats = self._db.get(self._classname, "speed_watcher", [])
        gain_chats = self._db.get(self._classname, "gain_watcher", [])
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        if chatid_str in norm_chats:
            norm_chats.remove(chatid_str)
            self._db.set(self._classname, "norm_watcher", norm_chats)
        if chatid_str in nr_chats:
            nr_chats.remove(chatid_str)
            self._db.set(self._classname, "nr_watcher", nr_chats)
        if chatid_str in dalek_chats:
            dalek_chats.remove(chatid_str)
            self._db.set(self._classname, "dalek_watcher", dalek_chats)
        if chatid_str in pitch_chats:
            pitch_chats.remove(chatid_str)
            self._db.set(self._classname, "pitch_watcher", pitch_chats)
        if chatid_str in vcanon_chats:
            vcanon_chats.remove(chatid_str)
            self._db.set(self._classname, "vcanon_watcher", vcanon_chats)
        if chatid_str in speed_chats:
            speed_chats.remove(chatid_str)
            self._db.set(self._classname, "speed_watcher", speed_chats)
        if chatid_str in gain_chats:
            gain_chats.remove(chatid_str)
            self._db.set(self._classname, "gain_watcher", gain_chats)
        await utils.answer(
            message,
            self.apo_lib.utils.get_str("vtauto_stopped", self.all_strings, message),
        )

    @loader.watcher("out", "only_media")
    async def watcher(self, message: Message):
        chatid = utils.get_chat_id(message)
        chatid_str = str(chatid)
        norm_chats = self._db.get(self._classname, "norm_watcher", [])
        nr_chats = self._db.get(self._classname, "nr_watcher", [])
        dalek_chats = self._db.get(self._classname, "dalek_watcher", [])
        pitch_chats = self._db.get(self._classname, "pitch_watcher", [])
        vcanon_chats = self._db.get(self._classname, "vcanon_watcher", [])
        speed_chats = self._db.get(self._classname, "speed_watcher", [])
        gain_chats = self._db.get(self._classname, "gain_watcher", [])
        chat = await message.get_chat()
        chattype = await getchattype(message)
        if (
            chatid_str not in nr_chats
            and chatid_str not in dalek_chats
            and chatid_str not in norm_chats
            and chatid_str not in pitch_chats
            and chatid_str not in vcanon_chats
            and chatid_str not in speed_chats
            and chatid_str not in gain_chats
        ):
            return
        if (
            chattype != "channel"
            and message.sender_id != self.tg_id
            or chattype == "channel"
            and not chat.admin_rights.delete_messages
        ):
            return
        if not message.voice or message.via_bot or message.forward:
            return
        if message.reply:
            reply = await message.get_reply_message()
        nr_lvl = self.config["nr_lvl"]
        pitch_lvl = self.config["pitch_lvl"]
        speed_lvl = self.config["speed_lvl"]
        gain_lvl = self.config["gain_lvl"]
        if chatid_str in dalek_chats:
            nr_lvl = 0.8
        if chatid_str in vcanon_chats:
            nr_lvl = 0.8
            pitch_lvl = -4.5
        msgs = await message.forward_to(self.tg_id)
        await self._client.delete_messages(chatid, message)
        file = io.BytesIO()
        file.name = msgs.file.name
        await self._client.download_file(msgs, file)
        filename = msgs.file.name or "voice"
        ext = msgs.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".ogg", "")
        else:
            filename_new = filename.replace(ext, "")
        file.seek(0)
        await self._client.delete_messages(self.tg_id, msgs)
        file.name = filename_new + ext
        filename, file_ext = os.path.splitext(file.name)
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".mp3", "1", "libmp3lame"
        )
        file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".wav", "1", "pcm_s16le"
        )
        file.seek(0)
        if (
            chatid_str in nr_chats
            or chatid_str in vcanon_chats
            or chatid_str in dalek_chats
        ):
            file, filename, file_ext = await audiodenoiser(
                file, filename, file_ext, nr_lvl
            )
            file.seek(0)
        if (
            chatid_str in norm_chats
            or chatid_str in vcanon_chats
            or chatid_str in dalek_chats
            or chatid_str in gain_chats
        ):
            file, filename, file_ext = await audionormalizer(
                file, filename, file_ext, gain_lvl
            )
            file.seek(0)
        if chatid_str in dalek_chats or chatid_str in vcanon_chats:
            file, filename, file_ext = await dalekvoice(file, filename, file_ext)
            file.seek(0)
        if chatid_str in pitch_chats or chatid_str in vcanon_chats:
            file, filename, file_ext = await audiopitcher(
                file, filename, file_ext, pitch_lvl
            )
            file.seek(0)
        if chatid_str in speed_chats:
            file, filename, file_ext = await audiospeedup(
                file, filename, file_ext, speed_lvl
            )
            file.seek(0)
        file, filename, file_ext = await audiohandler(
            file, filename, file_ext, ".ogg", "2", "libopus"
        )
        file.seek(0)
        file.name = filename + file_ext
        if reply:
            await self._client.send_file(chatid, file, voice_note=True, reply_to=reply)
        else:
            await self._client.send_file(chatid, file, voice_note=True)
