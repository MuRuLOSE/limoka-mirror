__version__ = (1, 0, 0)
# 	
# 	 @@@@@@    @@@@@@   @@@@@@@  @@@@@@@    @@@@@@   @@@@@@@@@@    @@@@@@   @@@@@@@   @@@  @@@  @@@       @@@@@@@@   @@@@@@
# 	@@@@@@@@  @@@@@@@   @@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@  @@@  @@@       @@@@@@@@  @@@@@@@
# 	@@!  @@@  !@@         @@!    @@!  @@@  @@!  @@@  @@! @@! @@!  @@!  @@@  @@!  @@@  @@!  @@@  @@!       @@!       !@@
# 	!@!  @!@  !@!         !@!    !@!  @!@  !@!  @!@  !@! !@! !@!  !@!  @!@  !@!  @!@  !@!  @!@  !@!       !@!       !@!
# 	@!@!@!@!  !!@@!!      @!!    @!@!!@!   @!@  !@!  @!! !!@ @!@  @!@  !@!  @!@  !@!  @!@  !@!  @!!       @!!!:!    !!@@!!
# 	!!!@!!!!   !!@!!!     !!!    !!@!@!    !@!  !!!  !@!   ! !@!  !@!  !!!  !@!  !!!  !@!  !!!  !!!       !!!!!:     !!@!!!
# 	!!:  !!!       !:!    !!:    !!: :!!   !!:  !!!  !!:     !!:  !!:  !!!  !!:  !!!  !!:  !!!  !!:       !!:            !:!
# 	:!:  !:!      !:!     :!:    :!:  !:!  :!:  !:!  :!:     :!:  :!:  !:!  :!:  !:!  :!:  !:!   :!:      :!:           !:!
# 	::   :::  :::: ::      ::    ::   :::  ::::: ::  :::     ::   ::::: ::   :::: ::  ::::: ::   :: ::::   :: ::::  :::: ::
# 	 :   : :  :: : :       :      :   : :   : :  :    :      :     : :  :   :: :  :    : :  :   : :: : :  : :: ::   :: : :
# 	
#                                             © Copyright 2024
#
#                                    https://t.me/Den4ikSuperOstryyPer4ik
#                                                  and
#                                          https://t.me/ToXicUse
#
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html
#
# meta developer: @AstroModules
# meta banner: https://raw.githubusercontent.com/Den4ikSuperOstryyPer4ik/Astro-modules/main/Banners/PCManager.jpg

from typing import Union
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall


class PCManagerMod(loader.Module):
	'''Управление вашим компьютером через юзербота'''
	strings = {"name": "PC-Manager"}

	def __init__(self):
		self.config = loader.ModuleConfig(
			loader.ConfigValue(
				'bot_username',
				None,
				doc=lambda: "Введите юзернейм вашего бота для управления ПК"
			)
		)

	async def client_ready(self):
		self.lib = await self.import_lib(
			'git.vsecoder.dev/-/raw/main/libs/AstroModules_Library.py',
			suspend_on_error=False,
		)


	@loader.command()
	async def addbot(self, message: Message):
		'''- добавить бота

 💎 Основные команды:'''
		await self.allmodules.commands["config"](
					await utils.answer(message, f"{self.get_prefix()}config PC-Manager")
				)
	@loader.command()
	async def tutor(self, message: Message):
		"""- туториал по подключению"""
		await utils.answer(message, "<emoji document_id=5787237370709413702>⚙️</emoji> <b>Туториал по настройке модуля:</b>\n\n@PC_AM_Tutor\n\nЕсли возникли трудности с установкой, пожалуйста, обратитесь в чат AstroModules ")

	@loader.command()
	async def pcoff(self, message: Message):
		"""- выключить компьютер""" 
		bot = self.config["bot_username"]
		call = await self.lib.message_g('🛑 Shutdown',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}')

	@loader.command()
	async def pcreboot(self, message: Message):
		"""- перезагрузить компьютер"""
		bot = self.config["bot_username"]
		call = await self.lib.message_g('🔄 Reboot',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}')

	@loader.command()
	async def pcinfo(self, message: Message):
		"""- просмотреть характеристики системы"""
		bot = self.config["bot_username"]
		call = await self.lib.message_q('💻 System Info',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}')

	@loader.command()
	async def pcip(self, message: Message):
		"""- просмотреть информацию об айпи адресе"""
		bot = self.config["bot_username"]
		call = await self.lib.message_q('🌐 IP Info',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}')

	@loader.command()
	async def pcscrin(self, message: Message):
		"""- сделать скриншот экрана"""
		bot = self.config['bot_username']
		call = await self.lib.message_g('/screenshot',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, '<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\nОтправка скриншота...')
		await message.respond(call)

	@loader.command()
	async def pcweb(self, message: Message):
		"""<ссылка> - открыть ссылку в браузере"""
		bot = self.config['bot_username']
		args = utils.get_args_raw(message)
		call = await self.lib.message_q(f'/browse {args}',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}\n\nСсылка: {args}')

	@loader.command()
	async def pcwebscrin(self, message: Message):
		"""- сделать снимок с веб-камеры

🔑 Дополнительно:"""
		bot = self.config['bot_username']
		call = await self.lib.message_g('/photo',
			bot,
			mark_read=True,
			delete=True
		)
		await utils.answer(message, '<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\nОтправка снимка...')
		await message.respond(call)

	@loader.command()
	async def pcalert(self, message: Message):
		"""<сообщение> - вывести на экран сообщение"""
		bot = self.config['bot_username']
		args = utils.get_args_raw(message)
		call = await self.lib.message_q(f'/alert {args}',
			bot,
			mark_read=True,
			delete=True
		)
		await message.respond(f'<emoji document_id=5787544344906959608>ℹ️</emoji> <b>[PC_Manager]</b> <emoji document_id=5787544344906959608>ℹ️</emoji>\n\n{call.text}')
		await message.delete()
	
	@loader.command()
	async def pcvol(self, message: Message):
		"""- управление звуком"""
		await self.inline.form(
			text="ℹ️ <b>[PC_Manager]</b> ℹ️\n\n<b>Мишкер громкости</b>",
			reply_markup=[
				[
					{
						"text": "10%",
						"callback": self.set_volume,
						"args": (10,)
					},
					{
						"text": "20%",
						"callback": self.set_volume,
						"args": (20,)
					},
					{
						"text": "30%",
						"callback": self.set_volume,
						"args": (30,)
					},
				],
				[
					{
						"text": "40%",
						"callback": self.set_volume,
						"args": (40,)
					},
					{
						"text": "50%",
						"callback": self.set_volume,
						"args": (50,)
					},
					{
						"text": "60%",
						"callback": self.set_volume,
						"args": (60,)
					},
				],
				[	
					{
						"text": "70%",
						"callback": self.set_volume,
						"args": (70,)
					},
					{
						"text": "80%",
						"callback": self.set_volume,
						"args": (80,)
					},
					{
						"text": "90%",
						"callback": self.set_volume,
						"args": (90,)
					},
				],
				[	
					{
						"text": "⬆️",
						"callback": self.set_volume,
						"args": ("up",)
					},			
					{
						"text": "100%",
						"callback": self.set_volume,
						"args": (100,)
					},
					{
						"text": "⬇️",
						"callback": self.set_volume,
						"args": ("down",)
					},
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": "close"
					}
				],
			],
			message=message,
		)

	@loader.command()
	async def pcmedia(self, message: Message):
		"""- управление музыкой"""
		await self.inline.form(
			text="ℹ️ <b>[PC_Manager]</b> ℹ️\n\n<b>Управление медиа</b>",
			reply_markup=[
				[
					{
						"text": "⏪",
						"callback": self.nazad
					},
					{
						"text": "⏯",
						"callback": self.pausa
					},
					{
						"text": "⏩",
						"callback": self.vpered
					},
				],
				[{"text": "🚫 Закрыть", "action": "close"}],
			],
			message=message,
		)
	

	async def set_volume(self, call: InlineCall, volume: Union[int, str]):
		bot = self.config['bot_username']
		await self.client.send_message(bot, f'/volume {volume}')
		return await call.answer("Успешно!", show_alert=False)

	async def nazad(self, call: InlineCall):
		bot = self.config['bot_username']
		await self.client.send_message(f'{bot}', '/key__prev')
		return await call.answer("Успешно!", show_alert=False)

	async def pausa(self, call: InlineCall):
		bot = self.config['bot_username']
		await self.client.send_message(f'{bot}', '/key__play')
		return await call.answer("Успешно!", show_alert=False)

	async def vpered(self, call: InlineCall):
		bot = self.config['bot_username']
		await self.client.send_message(f'{bot}', '/key__next')
		return await call.answer("Успешно!", show_alert=False)

																			# Tx...