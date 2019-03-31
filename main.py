import asyncio
import hashlib
import logging
import sys

import aiofiles
from aiohttp import ClientSession, TCPConnector
from pypeln import asyncio_task as aio

logging.basicConfig(level=logging.DEBUG)

urls = (f"https://intranet.upv.es/foto/getb/{i}.gif" for i in range(int(sys.argv[1])))
headers = {"Referer": "https://intranet.upv.es/pls/soalu/sic_al.lis"}
hash_not_available = (
    "12fc76fc961784a7568e6bbfe53559ec00e8819fdb807d44"
    "2735c465e938c5ee8ac060f7abe70c9fbe8b52d461379430"
    "637676399a793900d8221419fa5b50a5"
)


async def download(url, session):
    try:
        async with session.get(url, headers=headers) as response:
            response_file = await response.read()

            if hashlib.blake2b(response_file).hexdigest() != hash_not_available:
                file_name = url.split("/")[5]

                f = await aiofiles.open(f"photos/{file_name}", mode="wb")

                await f.write(await response.read())
                await f.close()

                logging.info(f"Downloaded {file_name}")
    except:
        pass


aio.each(
    download,
    urls,
    workers=1_000,
    on_start=lambda: ClientSession(connector=TCPConnector(limit=None)),
    on_done=lambda _status, session: session.close(),
    run=True,
)
