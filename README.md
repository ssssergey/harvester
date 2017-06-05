# Harvester
News aggregator which is supposed to be deployed on a server and be triggers by cron (or other similar tool).

It runs through a list of rss and filter the entries by title. A set of keywords is used for this purpose. Keywords 
can be changed and tuned for other fields.

Then selected articles are asyncronously downloaded, parsed and saved to db (Postgresql).

## Requirements
* aiohttp==2.1.0 - HTTP client/server for asyncio (only client is used here)
* aiopg==0.13.0 - library for accessing a PostgreSQL database from the asyncio
* beautifulsoup4==4.6.0 - library for pulling data out of HTML
* elasticsearch==5.4.0 - official low-level client for Elasticsearch
* feedparser==5.2.1 - universal feed parser, handles RSS, CDF, Atom feeds
* motor==1.1 - asynchronous Python driver for MongoDB
* python-dateutil==2.6.0 - extensions to the standard datetime module
* pytz==2017.2 - world timezone definitions for Python
* SQLAlchemy==1.1.10 - Object Relational Mapper
