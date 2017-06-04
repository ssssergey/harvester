import asyncio

from publishers import BasePublisher
from settings import logger_debug


async def main():
    subclasses = BasePublisher.__subclasses__()
    for subclass in subclasses:
        publisher = subclass()
        try:
            publisher.filter_links_from_rss()

            if publisher.entries_selected:
                to_do = [entry.download_entry() for entry in publisher.entries_selected]
                to_do_iter = asyncio.as_completed(to_do)
                for future in to_do_iter:
                    await future
            else:
                print('No valid news')
        except Exception as e:
            logger_debug.error('{}: {}'.format(e.__class__.__name__, e))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
