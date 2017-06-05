from aiopg.sa import create_engine
import sqlalchemy as sa
from psycopg2 import IntegrityError
from elasticsearch import Elasticsearch
# from elasticsearch_async import AsyncElasticsearch
# asynchronous elasticsearch-py-async cant be used here yet, because it depends on depricated version of aiohttp (< 2.0)

from settings import (TEXT_SIZE_LIMIT, USE_POSTGRESQL, USE_MONGODB, USE_ELASTICSEARCH, PG_DB, PG_USER, PG_PASSWORD,
                      MONGO_DB)

es_client = Elasticsearch()
# es_client = AsyncElasticsearch()

metadata = sa.MetaData()

tbl = sa.Table('tbl', metadata,
               sa.Column('id', sa.Integer, primary_key=True),
               sa.Column('rss', sa.String(255)),
               sa.Column('title', sa.Text()),
               sa.Column('body', sa.Text()),
               sa.Column('pub_time', sa.DateTime()),
               sa.Column('country', sa.String(255)),
               sa.Column('link', sa.Text()),
               )


async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS tbl (
                                  id SERIAL PRIMARY KEY,
                                  rss VARCHAR(255),
                                  title VARCHAR,
                                  body VARCHAR,
                                  pub_time VARCHAR(255),
                                  country VARCHAR(255),
                                  link VARCHAR,
                                  UNIQUE (link)
                                  )''')


async def save_entry(entry, logger_bucket=None):
    if len(entry.main_text) > TEXT_SIZE_LIMIT or entry.country == 'Другие':
        return False
    if USE_POSTGRESQL:
        await output_to_sql_async(entry)
    if USE_MONGODB:
        await output_to_mongodb_async(entry)
    if USE_ELASTICSEARCH:
        output_to_elasticsearch(entry)
        # await output_to_elasticsearch_async(entry)


async def output_to_sql_async(entry):
    async with create_engine(user=PG_USER,
                             database=PG_DB,
                             host='127.0.0.1',
                             password=PG_PASSWORD) as engine:
        await create_table(engine)

        async with engine.acquire() as conn:
            try:
                await conn.execute(
                    tbl.insert().values(rss=entry.publisher.name, title=entry.title, body=entry.main_text,
                                        pub_time=entry.publish_dt, country=entry.country, link=entry.link))
            except IntegrityError:
                pass


async def output_to_mongodb_async(entry):
    collection = MONGO_DB[entry.country]
    document = {'rss': entry.publisher.name, 'title': entry.title, 'body': entry.main_text,
                'pub_time': entry.publish_dt, 'link': entry.link}
    result = await collection.update(document, document, upsert=True)


def output_to_elasticsearch(entry):
    body = {'rss': entry.publisher.name, 'title': entry.title, 'body': entry.main_text,
            'pub_time': entry.publish_dt, 'link': entry.link}
    result = es_client.index(index='harvester', doc_type=entry.country, body=body)
    print(result)

# async def output_to_elasticsearch_async(entry):
#     body = {'rss': entry.publisher.name, 'title': entry.title, 'body': entry.main_text,
#             'pub_time': entry.publish_dt, 'link': entry.link}
#     result = await es_client.index(index='harvester', doc_type=entry.country, body=body)
#     print(result)
