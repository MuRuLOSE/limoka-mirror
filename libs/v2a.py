import asyncio
import logging
import os
import tempfile
from .. import loader
logger = logging.getLogger(__name__)

class V2ALib(loader.Library):
    developer = '@hikariatama'
    version = (1, 0, 0)

    async def convert(self, video: bytes, out: str) -> bytes:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, 'video.mp4'), 'wb') as f:
                f.write(video)
            proc = await asyncio.create_subprocess_exec('ffmpeg', '-i', os.path.abspath(os.path.join(tmpdir, 'video.mp4')), '-ab', '160k', '-ac', '2', '-ar', '44100', '-vn', os.path.join(tmpdir, out), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            if not os.path.isfile(os.path.join(tmpdir, out)):
                raise Exception('Error while converting')
            with open(os.path.join(tmpdir, out), 'rb') as f:
                return f.read()