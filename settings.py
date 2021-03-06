import os
import logging
from logging.handlers import RotatingFileHandler
import collections

from pytz import timezone
import motor.motor_asyncio

DEBUG = os.environ.get('DEBUG', False)

CURRENT_TIMEZONE = timezone('Europe/Moscow')

TEXT_SIZE_LIMIT = 5000

# paths
basedir = os.path.abspath(os.path.dirname(__file__))
log_file = os.path.join(basedir, 'debug.log')
keyword_file = os.path.join(basedir, 'keywords_militar.txt')
history_file = os.path.join(basedir, 'history.log')

# LOGGING
logger_debug = logging.getLogger('logger_debug')
formatter = logging.Formatter(
    '%(filename)s |%(funcName)s| [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
handler = RotatingFileHandler(log_file, mode='a', maxBytes=500 * 1024, backupCount=1, delay=0, encoding='utf8')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger_debug.addHandler(handler)

logger_history = logging.getLogger('logger_history')
handler2 = RotatingFileHandler(history_file, mode='a', maxBytes=500 * 1024, backupCount=1, delay=0, encoding='utf8')
handler2.setLevel(logging.INFO)
formatter2 = logging.Formatter('[%(asctime)s] | %(message)s')
handler2.setFormatter(formatter2)
logger_history.addHandler(handler2)

# STORAGES
USE_POSTGRESQL = os.environ.get('POSTGRESQL_HARVESTER', False)
USE_MONGODB = os.environ.get('MONGODB', False)
USE_ELASTICSEARCH = os.environ.get('ELASTICSEARCH', False)

# POSTGRESQL
PG_DB = os.environ.get('PG_NAME_HARVESTER')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASS')

# MONGODB
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = None
if USE_MONGODB:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST, MONGO_PORT)
    MONGO_DB = client['harvester_db']

# ELASTICSEARCH
ES_HOST = os.environ.get('ES_HOST', 'localhost')
ES_PORT = int(os.environ.get('ES_PORT', 9200))

STOP_WORDS = ['бокс[её]р', 'хоккеист', 'Бессмертн', 'зв[её]здны[а-я]{,2} войн', '\\bВойнов', '\\bПутин',
              'велик[а-я]{2} отечествен', 'втор[а-я]{2} миров', 'Война и мир', 'Лавров', 'Песков', 'Захарова', 'МО РФ:',
              'Минобороны РФ:', 'МИД РФ']

COUNTRIES_KEYWORDS = collections.OrderedDict([
    (('\\bАТО\\b', 'аваков', 'авдеевк', '\\bАзов\\b', 'алчевск', 'артемовск', 'бэтмен', 'бэтмэн',
      'Верховн[а-я]{,2} Рад[а-я]{,2}', 'винниц', 'волновах', '\\bВСУ\\b', 'горловк', 'гранитно',
      'дебальце', 'днепр', 'днр', 'донбас', 'донетч', 'закарпат',
      'донецк', 'дружковк', 'житомир', 'за ночь боевики', 'запорож', 'киборг', 'киев', 'краснодон', 'красном луче',
      'крым',
      'лнр', 'луганск', 'луганщин', 'львов', 'макеевк', 'мариупол', 'никишино', 'николаев', 'никопол', 'Новоросси[^й]',
      'одесс', 'одесч', 'ольховатк', 'парубий', 'полтав', 'полторак', 'порошенко', 'правого сектора', 'пушилин', 'СБУ',
      'семенченко',
      'славянск', 'снбо', 'старобешево', 'стаханов', 'счасть', 'турчинов', 'тымчук', 'украин', 'укроборон', 'харьков',
      'херсон', 'чернигов', 'черновц', 'яценюк', 'Весело', 'шахтерск', 'захарченко', 'геращенко', 'попасн', 'чермалык',
      'франковск',
      'зона боевых действий', 'лысенко', 'Изюм', 'Пески', '\\bполтав', 'красногоровк', 'марьинк', 'луценко',
      'тернополь', '\\bТорез', 'Айдар', 'ОУН',
      'углегорск', 'чернухино', 'лисичанск', 'докучаевск', 'Гнутово', 'Фащевк', 'краматорск', 'Ярош', 'Сартан',
      'Широкино', 'Басурин', 'ГПУ', 'ГПСУ', 'Саакашвили'), 'Украина'),
    (('азербайдж', 'Баку(?!\s*\-\s*АПА\.)', 'карабах', 'армян', 'ереван', 'Армени', 'бакинск', 'нахчыван', 'Агдаш',
      '\\bНардаран', 'Арцах', '\\bНКР\\b'), 'Азербайджан'),
    (('Абхази', 'вазиани', 'Гальск', '(?!Новости\-)Грузи[а-я]', 'грузин', 'кутаиси', 'сенаки', 'сухуми', 'тбилиси[^,]',
      'цхинвали', 'джавахет', 'чахалян', '\\bПоти\\b', '\\bПанкис', '\\bбатум', 'Аласан', 'Южн[а-я]{,2} Осет[а-я]{,2}',
      'Маргвелашвили',
      'Гарибашвили', 'Хидашели', 'Усупашвили', 'Гудаури', 'Сачхере', 'Крцаниси', 'Капанадзе'), 'Грузия'),
    (('анкар', '\\bРПК[^А-Я]', 'стамбул', 'турецк', 'турц', 'Аселсан', 'Отокар', 'Эрдоган', '\bPKK\b', 'Давутоглу'),
     'Турция'),
    (('IAI', '\\bГаз[аы]\\b', 'Ганц', 'Голанах', 'Голанск', 'Голаны', 'Гуш-Эцион', 'Машаль', 'Халхуль',
      'Яалон', 'беэр-шев', 'железный купол', 'иерусалим', 'израил', 'иуде[яи]', 'кнессет', 'либерман', 'магав',
      'нетаниягу', 'палестин', 'рахат', 'самари', 'сектор[а-я]{,3} газа', 'тель-авив', 'хайф', 'хамас', 'хеврон',
      'цахал', 'шабак'), 'Израиль'),
    (('Грозн', 'гудермес', 'дагестан', 'имарат', 'ингуш', 'кабард', 'КБР', 'кадыров', 'карабудах', 'карачаев',
      'махачкал', 'назран',
      'нальчик', 'Северн[а-я]{,2} Осет[а-я]{,2}', 'осетия', 'чечен', 'Чечн', 'хасавюрт', '\\bадыг', 'черкес', 'Хазбиев',
      'Чиркейск', 'пятигорск',
      'ставрополь', 'Северн[а-я]{,3} Кавказ[а-я]{,3}', 'владикавказ', 'дербент'), 'Северный Кавказ'),
    (('Иран', 'иранск', 'тегеран', 'Зариф', 'КСИР', '\\bИРИ\\b', 'Роухани', '\\ирано'), 'Иран'),
    (('\\bливан', 'бейрут', 'насралла', 'хизбалла'), 'Ливан'),
    (('молдав', 'кишенев', 'кишинев', 'приднестров', 'тирасполь', 'Молдов'), 'Молдавия'),
    (('Ирак[^л]', '\\bиракск', 'багдад', 'мосул', 'Дияла', 'Киркук', 'Тикрит', 'Рамади\\b', '\\bАнбар\\b'), 'Ирак'),
    (('афган', 'кандагар', 'кабул', 'кундуз'), 'Афганистан'),
    (('пакистан', 'исламабад', 'пешавар', 'техрике'), 'Пакистан'),
    (('Астан', '\\bказах', 'киргиз', 'кыргыз', 'таджик', 'туркмен', 'узбек', 'душанбе'), 'Средняя Азия'),
    (('\\bсири', 'алеппо', 'дамаск', 'кобани', 'нусра', 'ракк', 'башар', 'Асад', 'хасика', 'Пальмир', 'Дейр[ -]эз-Зор',
      'Латаки', 'Кунейтр', 'Хомс[а-я]{,2}', 'Дараа', 'Идлеб', '\\bХама\\b', '\\bХасаке\\b', 'Хмеймим', '\\bСАР\\b',
      'Камышли', '\\bPYD\\b'), 'Сирия'),
    (('\\bЛивии', '\\bливию', 'алжир', '\\bливийск', '\\bливия', '\\bтунис', 'марокк', 'туарег', 'мавритан'), 'Магриб'),
    (('египет', 'египт', '\\bкаир', 'синай', 'синая', 'синае', 'Шарм-эль-Шейх'), 'Египет'),
    (('бахрейн', 'йемен', 'катар', 'кувейт', 'оаэ', 'саудовск', '\\bоман', 'эр-рияд'), 'арабы ЗПЗ'),
    (('\\bливан', 'хезболла', 'бейрут'), 'Ливан'), (('\\bинди[^авг]', 'Дели ', 'мумбаи'), 'Индия'),
    (('иордан', '\\bАмман'), 'Иордания'),
    (('канад', 'оттав'), 'Канада'),
    (('\\bавстри', '\\bалбан', '\\bангли', '\\bафин', '\\bбалтик', '\\bбелград', '\\bбельг', '\\bберлин', '\\bболгар',
      '\\bвена\\b', '\\bвенгер', '\\bвенгр', '\\bвене ', '\\bгреци', '\\bдании', '\\bдатск', '\\bес\\b', '\\bиспан',
      '\\bитали', '\\bкипр', '\\bкосов[оес]', '\\bлатви', '\\bлитв[аеуы]', '\\bмилан', '\\bнато\\b', '\\bнемец',
      '\\bницц', '\\bпольс', '\\bриг[а-я]{,2}\\b', '\\bрим\\b', '\\bрима\\b', 'soir', 'бридлав', 'британ', 'брюссел',
      'бундес', 'варшав', 'герман', 'голланд', 'греческ', 'европ[^о]', 'евросоюз', 'женев[ае]', 'ирланд', 'исланд',
      'итальян', 'копенгаген', 'лейпциг', 'литовск', 'лондон', 'мадрид', 'македони', 'марсел', 'меркель', 'нидерланд',
      'норвеги', 'норвежск', 'олланд', 'париж', 'польш', 'португал', 'расмуссен', 'румын', 'сааб', 'североатлант',
      'серби', 'скопье', 'словак', 'словен', 'стокгольм', 'талес', 'финлянд', 'финск', 'франкфурт', 'франц[а-я]{2,}',
      'фрг',
      'хорват', 'цюрих', 'черногор', 'чехи', 'чешск', 'швед', 'швейцар', 'швеци', 'эстон', '\\bмальт[аеуы]\\b',
      '\\bандор[аеуы]\\b', 'Кэмерон'), 'Европа'),
    (('китай', 'китае', 'китая', 'китаю', 'пекин', 'гонконг', 'КНР', 'тайван'), 'Китай'),
    (('Корея', 'Кореи', 'Корею', 'кндр', 'пхеньян', 'сеул', 'корейск', 'Ким Чен'), 'Корея'),
    (('япон', 'токио', 'Абэ', 'Синдзо'), 'Япония'),
    (('американ', 'вашингтон', 'Обама', 'пентагон', 'США', 'теннесси', 'цру', 'маккейн', 'нью-йорк', 'техас', 'канзас',
      'керри',
      'госсекретар', 'калифорн', 'nasa', 'огайо', 'фбр', 'флорид', 'АНБ', 'НАСА', 'Райс', 'Байден', 'госдеп',
      'Lockheed',
      'Локхид Мартин', 'Рейтеон', 'Балтимор'), 'США'),
    (('австрал', '\\bсидне', 'мельбурн'), 'Австралия'),
    (('бруней', 'вьетнам', 'индонез', 'камбодж', '\\bлаос', 'малайз', 'малазий', 'мьянм', 'сингапур', 'таиланд',
      '\\bтимор', 'филиппин',
      'бангкок', 'бангладеш', ' тайск', '\\bнепал'), 'ЮгоВосточная Азия'),
    (('аргентин', 'болив', 'бразил', 'венесуэл', 'колумб', 'мексик', '\\bперу', 'чилий', 'парагва', 'уругва',
      'монтевидео', 'сантьяго',
      ' чилийск', 'Чили', 'Мехико', 'карибск', 'никарагуа', '\\bкубинск', 'Куб[а-я]\\b', 'эквадор'),
     'Латинская Америка'),
    (('боко харам', 'бурунди', 'конго', 'либери', 'могадишо', '\\bнигер', 'сомалий', '\\bсудан', 'сьерра-леоне',
      'шабаб', 'Мали\\b', 'танзан', 'камерун', 'боко-харам', 'замби', 'гвине', 'малийск', 'африк', '\\bкени[яюйи]',
      'сенегал',
      '\\bангол', 'ЦАР', 'Бенин', 'Габон', 'ЮАР', 'эфиоп', 'джибут', '\\bБуркина', '\\bЧаде\\b', '\\bЧада\\b',
      'Сомали'), 'Африка'),
])
