# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GitItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    site_url = scrapy.Field()
    stars = scrapy.Field()
    forks = scrapy.Field()
    watching = scrapy.Field()
    commits = scrapy.Field()
    last_commit_author = scrapy.Field()
    last_commit_message = scrapy.Field()
    last_commit_datetime = scrapy.Field()
    releases = scrapy.Field()
    last_release_ver = scrapy.Field()
    last_release_change_log = scrapy.Field()
    last_release_datetime = scrapy.Field()
