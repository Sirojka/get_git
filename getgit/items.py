# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass


@dataclass
class Commit:
    author: str = ''
    title: str = ''
    date_time: str = ''


@dataclass
class Release:
    ver: str = ''
    change_log: str = ''
    date_time: str = ''


class GitItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    site_url = scrapy.Field()
    stars = scrapy.Field()
    forks = scrapy.Field()
    watching = scrapy.Field()
    commits = scrapy.Field()
    last_commit = Commit()
    releases = scrapy.Field()
    last_release = Release()
