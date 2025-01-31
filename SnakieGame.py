#              © Copyright 2024
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html
# meta developer: @shiro_hikka

from .. import loader, utils
from telethon.tl.types import Message
import random
from ..inline.types import InlineCall

class SnakieMod(loader.Module):
    """"""
    strings = {
        "name": "SnakeGame",
        "start_text": "Game"
    }

    def markupGenerate(self):
        row_markup = []
        for i in range(8):
            row_markup.append(
                {
                    "text": "⬛",
                    "callback": None
                }
            )

        markup = []
        for i in range(8):
            markup.append(
                row_markup
            )

        

    def validate_pos(n_apple, apple, snake):
        if n_apple == apple or n_apple == snake:
            return False
        elif:
            if any(i == n_apple[0] for i in [snake[0], snake[0]+1, snake[0]-1]):
                if any(i == n_apple[1] for i in [snake[1], snake[1]+1, snake[1]-1]):
                    return False
        elif:
            if any(i == n_apple[0] for i in [apple[0], apple[0]+1, apple[0]-1]):
                if any(i == n_apple[1] for i in [apple[1], apple[1]+1, apple[1]-1]):
                    if any(i == apple[0] for i in [snake[0], snake[0]+1, snake[0]-1]):
                        if any(i == apple[1] for i in [snake[1], snake[1]+1, snake[1]-1]):
                            return False
        else:
            return True

    def appleSpawn(self, pos):
        for i in pos.reply_markup.rows:
            for j in i.buttons:
                if j.text == "🍎":
                    apple_pos = (i, j)
                elif j.text == "🐍":
                    snake_pos = (i, j)
        return rand(apple_pos, snake_pos)

    def rand(apple_pos, snake_pos)
        next_apple_pos = (random.randrange(0, 7), random.randrange(0, 7))
        valid = validate_pos(next_apple_pos, apple_pos, snake_pos)
        if valid:
            return (next_apple_pos, snake_pos)
        else:
            rand(apple_pos, snake_pos)

    async def up(self, call: InlineCall):
        apple_spawn = appleSpawn(call)
        markup = markupGenerate()

        markup.append(
            [
                {
                    "text": "­­­­­­­­",
                    "callback": None
                },
                {
                    "text": "⬆",
                    "callback": self.up(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "⬅",
                    "callback": self.left(call)
                },
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "➡",
                    "callback": self.right(call)
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "⬇",
                    "callback": self.down(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )

        markup[apple_spawn[1][0]-1][apple_spawn[1][1]] = "🐍"
        markup[apple_spawn[0][0]][apple_spawn[0][1]] = "🍎"

        await call.edit(
            text=self.strings["start_text"],
            reply_markup=markup
        )

    async def left(self, call: InlineCall):
        apple_spawn = appleSpawn(call)
        markup = markupGenerate()

        markup.append(
            [
                {
                    "text": "­­­­­­­­",
                    "callback": None
                },
                {
                    "text": "⬆",
                    "callback": self.up(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "⬅",
                    "callback": self.left(call)
                },
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "➡",
                    "callback": self.right(call)
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "⬇",
                    "callback": self.down(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )

        markup[apple_spawn[1][0]][apple_spawn[1][1]-1] = "🐍"
        markup[apple_spawn[0][0]][apple_spawn[0][1]] = "🍎"

        await call.edit(
            text=self.strings["start_text"],
            reply_markup=markup
        )

    async def right(self, call: InlineCall):
        apple_spawn = appleSpawn(call)
        markup = markupGenerate()

        markup.append(
            [
                {
                    "text": "­­­­­­­­",
                    "callback": None
                },
                {
                    "text": "⬆",
                    "callback": self.up(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "⬅",
                    "callback": self.left(call)
                },
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "➡",
                    "callback": self.right(call)
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "⬇",
                    "callback": self.down(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )

        markup[apple_spawn[1][0]][apple_spawn[1][1]+1] = "🐍"
        markup[apple_spawn[0][0]][apple_spawn[0][1]] = "🍎"

        await call.edit(
            text=self.strings["start_text"],
            reply_markup=markup
        )

    async def down(self, call: InlineCall):
        apple_spawn = appleSpawn(call)
        markup = markupGenerate()

        markup.append(
            [
                {
                    "text": "­­­­­­­­",
                    "callback": None
                },
                {
                    "text": "⬆",
                    "callback": self.up(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "⬅",
                    "callback": self.left(call)
                },
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "➡",
                    "callback": self.right(call)
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "⬇",
                    "callback": self.down(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )

        markup[apple_spawn[1][0]+1][apple_spawn[1][1]] = "🐍"
        markup[apple_spawn[0][0]][apple_spawn[0][1]] = "🍎"

        await call.edit(
            text=self.strings["start_text"],
            reply_markup=markup
        )

    async def snakecmd(self, message: Message):
        """"""
        apple_spawn = rand((0, 0), (6, 5))
        markup = markupGenerate()

        markup.append(
            [
                {
                    "text": "­­­­­­­­",
                    "callback": None
                },
                {
                    "text": "⬆",
                    "callback": self.up(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "⬅",
                    "callback": self.left(call)
                },
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "➡",
                    "callback": self.right(call)
                }
            ]
        )
        markup.append(
            [
                {
                    "text": "",
                    "callback": None
                },
                {
                    "text": "⬇",
                    "callback": self.down(call)
                },
                {
                    "text": "",
                    "callback": None
                }
            ]
        )

        await self.inline.form(
            text=self.strings["start_text"],
            message=message,
            reply_markup=markup
        )