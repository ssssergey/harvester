# Harvester
News aggreggator which is supposed to be deployed on a server and be triggers by cron (or other similar tool).

It runs through a list of rss and filter the entries by title. A set of keywords is used for this purpose. Keywords 
can be changed and tuned for other fields.

Then selected articles are asyncronously downloaded, parsed and saved to db (Postgresql).

