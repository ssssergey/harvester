import re
from dateutil import parser
import asyncio

import feedparser

from entries import Entry
from settings import STOP_WORDS, history_file, keyword_file, CURRENT_TIMEZONE, logger_debug


class BasePublisher():
    """ This base class will be inherited by concrete classes of publishers """
    encoding = 'utf-8'
    name = None
    rss = None
    entries_selected = []

    def filter_links_from_rss(self):
        """
        Download rss feed and filter it's entries
        """
        try:
            rss_data = feedparser.parse(self.rss)
        except Exception as e:
            logger_debug.error('{}: {}'.format(e.__class__.__name__, e))
        else:
            if len(rss_data['entries']):
                for entry in rss_data.get('entries'):
                    try:
                        publish_dt = parser.parse(entry.published).astimezone(CURRENT_TIMEZONE)
                    except Exception as e:
                        logger_debug.error('{}: {}'.format(e.__class__.__name__, e))
                        continue
                    try:
                        if not self.is_in_history(entry.link) and self.matches_keyword(entry.title):
                            self.entries_selected.append(Entry(entry.link, entry.title, publish_dt, self))
                    except AttributeError as e:
                        logger_debug.error('{}: {}'.format(e.__class__.__name__, e))
                        continue

    def matches_keyword(self, entry_title):
        """ If the entry_title matches any theme keyword, return True """
        keywords_list = self.get_keywords_list()
        for word in keywords_list:
            p = re.compile(word)
            if p.search(entry_title.lower()) or p.search(entry_title):
                # If the entry matches any stop keyword, return False
                for stop_word in STOP_WORDS:
                    p1 = re.compile(stop_word)
                    if p1.search(entry_title.lower()) or p1.search(entry_title):
                        return False
                return True
        return False

    def is_in_history(self, entry_link):
        """ If the entry link have already been downloaded, return False """
        with open(history_file, "a+", encoding='utf-8-sig') as f:
            f.seek(0)
            history_list = f.readlines()
        if any(entry_link in line for line in history_list):
            return True
        return False

    def get_keywords_list(self):
        with open(keyword_file, "a+", encoding='utf-8-sig') as f:
            f.seek(0)
            keywords = f.readlines()
            keywords = [l.strip() for l in keywords]
        return keywords

    def get_divs(self, soup, div_classes, tag='div'):
        divs = []
        for cls in div_classes:
            divs.append(soup.find(tag, {'class': cls}))
        divs = [div for div in divs if div]
        return divs

    def get_main_text(self, soup, div_classes, tag='div', recursive=False):
        main_text = ''
        divs = self.get_divs(soup, div_classes, tag=tag)
        for div in divs:
            for everyitem in div.findAll('p', recursive=recursive):
                main_text += '\n' + everyitem.text
        return main_text


########################################################################################

class ApaAz(BasePublisher):
    name = 'APA.AZ'
    rss = 'http://ru.apa.az/rss'

    def is_in_history(self, entry_link):
        entry_link = entry_link.replace('http://az.apa', 'http://ru.apa')
        super().is_in_history(entry_link)

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['content'])
        return main_text


class Apsny(BasePublisher):
    encoding = 'cp1251'
    name = 'Грузия-онлайн'
    rss = 'http://apsny.ge/RSS.xml'

    def parse_body(self, soup, main_text=''):
        for trash in soup.findAll('a'):
            trash.decompose()
        for trash in soup.findAll('strong'):
            trash.decompose()
        for everyitem in soup.find('td', {'class': 'newsbody'}).findAll('div', {'class': 'txt-item-news'}):
            main_text += '\n' + everyitem.text
        return main_text


class Camto(BasePublisher):
    encoding = 'cp1251'
    name = 'ЦАМТО'
    rss = 'http://www.armstrade.org/export/news.xml'

    def parse_body(self, soup, main_text=''):
        if '401' in soup.html.head.title.text:
            main_text = 'ПЛАТНАЯ СТАТЬЯ'
        else:
            for everyitem in soup.find('div', {'class': 'content'}).find('div', {'class': 'mainnews'}).findAll('div'):
                main_text += '\n' + everyitem.text
        return main_text


class Irna(BasePublisher):
    name = 'ИРНА'
    rss = 'http://irna.ir//ru/rss.aspx?kind=701'

    def parse_body(self, soup, main_text=''):
        main_text += '\n' + soup.find('h3', {
            'id': 'ctl00_ctl00_ContentPlaceHolder_ContentPlaceHolder_NewsContent1_H1'}).text
        main_text += '\n' + soup.find('p', {
            'id': 'ctl00_ctl00_ContentPlaceHolder_ContentPlaceHolder_NewsContent1_BodyLabel'}).text
        return main_text


class Kommersant(BasePublisher):
    encoding = 'cp1251'
    name = 'Коммерсант'
    rss = 'http://www.kommersant.ru/RSS/news.xml'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('p', {'class': 'b-article__text'}):
            main_text += '\n' + everyitem.text
        return main_text


class MigNews(BasePublisher):
    encoding = 'cp1251'
    name = 'МигНьюс'
    rss = 'http://www.mignews.com/export/mig_export3.html'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('noindex', recursive=False):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('iframe'):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('div', {'class': 'addthis_toolbox addthis_default_style pad2'}):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('ul'):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('h5'):
            everyitem.replaceWith('')
        if soup.find('div', {'class': 'textnews'}):
            main_text = soup.find('div', {'class': 'textnews'}).text + '\n'
        elif soup.find('div', {'id': 'leftc'}):
            main_text = soup.find('div', {'id': 'leftc'}).text + '\n'
        return main_text


class NewsAsia(BasePublisher):
    encoding = 'cp1251'
    name = 'News-Asia'
    rss = 'http://www.news-asia.ru/rss/all'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['content'])
        return main_text


class RussiaToday(BasePublisher):
    name = 'RussiaToday'
    rss = 'http://russian.rt.com/rss/'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('p', {'class': 'disclaimer'}):
            everyitem.replaceWith('')
        main_text = self.get_main_text(soup, ['article__summary', 'article__text'])
        return main_text


class Korrespondent(BasePublisher):
    name = 'Корреспондент'
    rss = 'http://k.img.com.ua/rss/ru/ukraine.xml'

    def parse_body(self, soup, main_text=''):
        main_text = soup.find('div', {'class': 'post-item__text'}).text
        return main_text


class Unian(BasePublisher):
    name = 'УНИАН'
    rss = 'http://rss.unian.net/site/news_rus.rss'

    def parse_body(self, soup, main_text=''):
        main_text_list = []
        if soup.find('div', {'class': 'article_body'}):
            for everyitem in soup.find('div', {'class': 'article_body'}).findAll('p', recursive=False):
                if "Читайте также" not in everyitem.text:
                    main_text_list.append(everyitem)
        if soup.find('div', {'class': 'article-text'}):
            for everyitem in soup.find('div', {'class': 'article-text'}).findAll('p', recursive=False):
                if "Читайте также" not in everyitem.text:
                    main_text_list.append(everyitem)
        if main_text == '' and soup.find('span', {'itemprop': 'articleBody'}):
            for everyitem in soup.find('span', {'itemprop': 'articleBody'}).findAll('p', recursive=False):
                if "Читайте также" not in everyitem.text:
                    main_text_list.append(everyitem)
        main_text_list = [i.text.strip() for i in main_text_list if i and i.text]
        main_text = '\n'.join(main_text_list)
        return main_text


class Ukrinform(BasePublisher):
    name = 'Укринформ'
    rss = 'http://www.ukrinform.ru/rss/'

    def parse_body(self, soup, main_text=''):
        divs = self.get_divs(soup, ['newsText'], tag='article')
        for div in divs:
            for everyitem in div.findAll('p', recursive=False):
                if "Читайте также:" not in everyitem.text:
                    main_text += '\n' + everyitem.text
        return main_text


class RBKRussia(BasePublisher):
    name = 'РБК'
    rss = 'http://static.feed.rbc.ru/rbc/internal/rss.rbc.ru/rbc.ru/mainnews.rss'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['article__text'])
        return main_text


class BBC(BasePublisher):
    name = 'Би-Би-Си'
    rss = 'http://www.bbc.co.uk/russian/index.xml'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['story-body__inner', 'map-body', 'story-body'])
        return main_text


class Lenta(BasePublisher):
    name = 'Лента.ру'
    rss = 'http://lenta.ru/rss'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.find('div', {'itemprop': 'articleBody'}).findAll('p'):
            main_text += '\n' + everyitem.text
        return main_text


class Rian(BasePublisher):
    name = 'РИА-Новости-Украина'
    rss = 'http://rian.com.ua/export/rss2/politics/index.xml'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('p', {'style': 'text-align: center;'}):
            everyitem.replaceWith('')
        for everyitem in soup.find('div', {'itemprop': 'articleBody'}).findAll('p'):
            main_text += '\n' + everyitem.text
        return main_text


class Trend(BasePublisher):
    name = 'Тренд'
    rss = 'http://www.trend.az/feeds/index.rss'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.find('div', {'itemprop': 'articleBody'}).findAll('p'):
            if "@www_Trend_Az" not in everyitem.text and "agency@trend.az" not in everyitem.text:
                main_text += '\n' + everyitem.text
        return main_text


class KavkazUzel(BasePublisher):
    name = 'Кавказский узел'
    rss = 'http://www.kavkaz-uzel.ru/articles.rss/'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('div', {'class': 'lt-feedback_banner pull-right hidden-phone'}):
            everyitem.replaceWith('')

        main_text = self.get_main_text(soup, ['articles-body'])
        return main_text


class Vedomosti(BasePublisher):
    name = 'Ведомости'
    rss = 'http://www.vedomosti.ru/newsline/out/rss.xml'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['b-news-item__text b-news-item__text_one'])
        return main_text


class ItarTass(BasePublisher):
    name = 'ИТАР-ТАСС'
    rss = 'http://itar-tass.com/rss/v2.xml'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('div', {'class': 'b-gallery-widget-item'}):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('div', {'class': 'b-links printHidden'}):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('div', {'class': 'b-links b-links_mini b-links_right printHidden'}):
            everyitem.replaceWith('')
        for everyitem in soup.findAll('a', {'target': '_blank'}):
            everyitem.replaceWith('')

        main_text = self.get_main_text(soup, ['b-material-text__l'])
        return main_text


class Rosbalt(BasePublisher):
    name = 'Росбалт'
    rss = 'http://www.rosbalt.ru/feed/'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['newstext'])
        return main_text


class VPK(BasePublisher):
    name = 'ВПК'
    rss = 'http://vpk-news.ru/feed'

    def parse_body(self, soup, main_text=''):
        div = soup.find('div', {'class': 'field-name-body'})
        main_text = self.get_main_text(div, ['field-item even'])
        return main_text


class Fergana(BasePublisher):
    name = 'Фергана'
    rss = 'http://www.fergananews.com/rss.php'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('div', {'id': 'text'}):
            main_text += '\n' + everyitem.text
        return main_text


class Sputnik(BasePublisher):
    name = 'Спутник'
    rss = 'https://sputnik-georgia.ru/export/rss2/archive/index.xml'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.findAll('div', {'class': 'b-inject'}):
            everyitem.replaceWith('')
        main_text = self.get_main_text(soup, ['b-article__text'])
        return main_text


class ApsnyPress(BasePublisher):
    name = 'Апсны-Пресс'
    rss = 'http://www.apsnypress.info/news/rss/'

    def parse_body(self, soup, main_text=''):
        main_text = soup.find('div', {'class': 'detail_text'}).text
        return main_text


class Sana(BasePublisher):
    name = 'САНА'
    rss = 'http://sana.sy/ru/?feed=rss2'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['entry'])
        return main_text


class DAN(BasePublisher):
    name = 'ДАН'
    rss = 'http://dan-news.info/feed'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['entry'])
        return main_text


class Anadolu(BasePublisher):
    name = 'Анадолу'
    rss = 'http://aa.com.tr/ru/rss/default?cat=live'

    def parse_body(self, soup, main_text=''):
        main_text = self.get_main_text(soup, ['article-post-content'])
        return main_text


class ArmenPress(BasePublisher):
    name = 'Арменпресс'
    rss = 'http://armenpress.am/rus/rss/news/'

    def parse_body(self, soup, main_text=''):
        for everyitem in soup.find('span', {'itemprop': 'articleBody'}).findAll('p'):
            main_text += '\n' + everyitem.text
        return main_text


if __name__ == '__main__':
    publisher = Lenta()
    publisher.filter_links_from_rss()
    print('*' * 100)
    # for i in producer.entries_selected:
    # print(i.title)

    if publisher.entries_selected:
        loop = asyncio.get_event_loop()
        aw = asyncio.wait([entry.download_entry() for entry in publisher.entries_selected])
        loop.run_until_complete(aw)
    else:
        print('No valid news')
