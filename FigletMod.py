#
#█▀█ █▀▀ █▄░█ █▀▀ █▀▀ █▀█ █ █▄░█
#█▀▀ ██▄ █░▀█ █▄█ █▄█ █▀▄ █ █░▀█
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @penggrin
# meta banner: https://raw.githubusercontent.com/darkmodules/assets/master/FigletMod.png
# scope: hikka_only
# requires: pyfiglet

from .. import loader, utils
import logging

from pyfiglet import Figlet, FigletFont, FontNotFound

logger = logging.getLogger(__name__)


@loader.tds
class FigletMod(loader.Module):
    """With this module you can easily draw some pretty ASCII text (Some fonts OR longs texts may look weird on some devices)"""

    strings = {
        "name": "FigletMod",
        "here_is_figlet": "❤️ Here is your figlet:",
        "here_is_fonts": "❤️ Here is all of my fonts:",
        "font_not_found": "❌ Cant find the font (use <code>.figletfonts</code> to see all of them):",
        "config_default_font": "Default Figlet Font",
    }

    strings_ru = {
        "here_is_figlet": "❤️ Вот ваш figlet:",
        "here_is_fonts": "❤️ Вот все мои шрифты:",
        "font_not_found": "❌ Не могу найти нужный шрифт (используйте <code>.figletfonts</code> чтобы увидеть все доступные шрифты):",
        "config_default_font": "Стандартный Figlet Шрифт",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_font",
                "standard",
                lambda: self.strings("config_default_font"),
                validator=loader.validators.String(),
            ),
        )

    @loader.command(ru_doc="- Показать все доступные шрифты")
    async def figletfontscmd(self, message):
        """- Show all of the fonts available"""
        result = f"{self.strings('here_is_fonts')} | "
        for font in sorted(FigletFont.getFonts()):
            result += f"{font} | "
        await utils.answer(message, result)

    @loader.command(ru_doc="- [font:str OR -] <text:str> - (ИСПОЛЬЗОВАТЬ ТОЛЬКО АНГЛИЙСКИЕ БУКВЫ И СИМВОЛЫ) Нарисовать figlet текст с указаным шрифтом, либо со стандартным (Figlet это что-то вроде ASCII арта)")
    async def figletcmd(self, message):
        """[font:str OR -] <text:str> - Draw an figlet text with the font that you set, or a standart one (Figlet is some sort of ASCII-Art)"""
        args = utils.get_args(message)
        font = args[0] if args[0] != "-" else self.config["default_font"]

        try:
            result = f"{self.strings('here_is_figlet')}<code>\n{Figlet(font=font).renderText(' '.join(args[1:]))}\n</code>"
        except FontNotFound:
            result = self.strings("font_not_found")

        await utils.answer(message, result)
