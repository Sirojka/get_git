#!/usr/bin/python3
# -*- coding: utf-8 -*-
# coding: utf8

"""
Copyright: (c) 2022, Siarhei Straltsou
init release 2022-07-12
https://github.com scraper - the program for scraping info about GitHub account/repo using api/html
"""

import os
from urllib.parse import urlparse
import scrapy
from ..items import GitItem


class GitSpider(scrapy.Spider):

    name = 'gitcrawler'
    allowed_domains = ['github.com']

    links = list()

    custom_settings = {
    #     'LOG_FILE': '/var/log/getgit_log.log',
         'LOG_LEVEL': 'INFO'
    }

    test_links = [
        'https://github.com/ronggang',
        'https://github.com/scrapy/scrapy'
        ]
    update_asin_cache = set()
    global_asin_cache = set()
    items_cache = dict()
    sub_dept = dict()

    def __init__(self, ext_args):
        self.ext_args = ext_args
        super().__init__()

    def check_link(self, link):
        api_url = None
        is_account = False
        parsed_url = urlparse(url=link)
        if parsed_url.netloc == 'github.com':
            url_path = parsed_url.path.strip('/').lstrip('/')
            url_path_chunks = url_path.split('/')
            if len(url_path_chunks) == 1:
                api_url = 'https://api.github.com/users/{}'.format(*url_path_chunks)
                is_account = True
            elif len(url_path_chunks) == 2:
                api_url = 'https://api.github.com/repos/{}/{}'.format(*url_path_chunks)
        else:
            self.logger.error('Bad link: {}'.format(link))
        return api_url, is_account

    def start_requests(self):
        self.logger.info('Spider version: {}'.format(self.settings.get('VERSION')))
        self.logger.info(self.crawler.stats.get_stats())
        if self.ext_args.test:
            self.links = self.test_links
            self.logger.warning('Running in TEST MODE!!! Will use test list of links, {} items.'.format(
                len(self.links)))
        for link in self.links:
            url, url_type = self.check_link(link=link)
            if url:
                self.logger.info('URL: {}'.format(url))
                yield scrapy.Request(url=url, callback=self.parse, meta={'account': url_type})

    def parse(self, response, **kwargs):
        account = response.meta.get('account')
        account_type = 'account' if account else 'repository'
        resp_data = response.json()
        item = GitItem()
        item['title'] = resp_data.get('name')
        item['description'] = resp_data.get('description')
        item['site_url'] = resp_data.get('html_url')
        item['stars'] = resp_data.get('stargazers_count')
        item['forks'] = resp_data.get('forks_count')
        item['watching'] = resp_data.get('watchers_count')
        # item['commits'] = resp_data.get('')
        # item['last_commit'] = Commit()
        # item['releases'] = resp_data.get('')
        # item['last_release'] = Release()
        self.logger.info('Link type: {}, title: {}, desc: {}, url: {}, *: {}, fork: {}, watch: {},'.format(
            account_type, *item.values()))
        # yield item
