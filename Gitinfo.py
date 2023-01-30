#
#█▀▄ ▀█ █ █▀█ █░█  █▀▀ ▄▀█ █▄█
#█▄▀ █▄ █ █▀▄ █▄█  █▄█ █▀█ ░█░
# 🔒 Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @dziru
# scope: hikka_only
# version: 1.0

import requests
from .. import utils, loader

class GitInfoMod(loader.Module):
    """Get Github user info, simply type username"""

    strings = {
        "name": "GitInfo",
    }

    async def gitinfocmd(self, message):
        """<username>"""
        args = utils.get_args_raw(message)
        gitapi = "https://api.github.com/users/{}".format(args)
        s = requests.get(gitapi)
        if s.status_code != 404:
            b = s.json()
            avatar_url = b["avatar_url"]
            html_url = b["html_url"]
            name = b["name"]
            blog = b["blog"]
            location = b["location"]
            bio = b["bio"]
            created_at = b["created_at"]
            await self._client.send_file(message.chat_id, caption="<b>Name: </b><code>{}</code>\n<b>Link: </b><code>{}</code>\n\n<b>Blog: </b><code>{}</code>\n<b>Location: </b><code>{}</code>\n\n<b>Bio: </b><code>{}</code>\n<b>Profile Created: </b><code>{}</code>".format(name, html_url, blog, location, bio, created_at), file=avatar_url, force_document=False, allow_cache=False, reply_to=message)
            await message.delete()
        else:
            await message.edit("`{}`: {}".format(args, s.text))