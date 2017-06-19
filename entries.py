import re

import async_timeout
from bs4 import BeautifulSoup

from settings import COUNTRIES_KEYWORDS, logger_history, logger_debug
from storage import save_entry


class Entry():
    def __init__(self, link, title, publish_dt, publisher):
        self.link = link
        self.title = title
        self.publish_dt = publish_dt
        self.publisher = publisher
        self.main_text = ''
        self.country = 'Другие'

    async def download_entry(self, session):
        print('Start downloading {}'.format(self.link))
        try:
            response = await session.request('GET', self.link, timeout=20)
            print('Finish downloading {}'.format(self.link))
            body = await response.read()
            body = body.decode(encoding=self.publisher.encoding)
        except Exception as e:
            logger_debug.error('{}: {}'.format(e.__class__.__name__, self.publisher.name))
            return
        else:
            soup = BeautifulSoup(body, "html.parser")
            for script in soup.findAll('script'):  # Delete all js scripts from soup
                script.decompose()
            for style in soup.findAll('style'):  # Delete all css styles from soup
                style.decompose()
            try:
                self.main_text = self.publisher.parse_body(soup) or ''
            except AttributeError as e:
                logger_debug.error('{}: Parse Error: {}'.format(e.__class__.__name__, self.link))
                return
            self.strip_main_text()
            print(self.title)
            print(self.link)
            print(self.main_text)
            self.define_country()
            await save_entry(self)
            logger_history.warning(self.link)

    def define_country(self):
        """
        First try to define country by title, then (if not failed to define) by main_text
        """
        self.define_country_by_keywords(self.title)
        if self.country == 'Другие':
            # Only first part of the article is relevant for defining country
            self.define_country_by_keywords(self.main_text[:350])

    def define_country_by_keywords(self, text):
        for keywords in COUNTRIES_KEYWORDS.items():
            for keyword in keywords[0]:
                p = re.compile(keyword)
                if p.search(text) or p.search(text.lower()):
                    self.country = keywords[1]

    def strip_main_text(self):
        """ Remove empty lists and trailing spaces """
        self.main_text = "\n".join([line.strip() for line in self.main_text.split('\n') if line.strip()])
