import asyncio

import aiohttp

from publishers import BasePublisher
from settings import logger_debug


async def main(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        subclasses = BasePublisher.__subclasses__()
        for subclass in subclasses:
            publisher = subclass()
            try:
                await publisher.filter_links_from_rss(session)
            except Exception as e:
                logger_debug.error('{}: {}'.format(e.__class__.__name__, e))
                continue


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
