#!/usr/bin/python3
# -*- coding: utf-8 -*-
# coding: utf8

"""
Copyright: (c) 2022, Siarhei Straltsou
init release 2022-07-12
https://github.com scraper - the program for scraping info about GitHub account/repo using api/html
"""

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
        full_name = resp_data.get('full_name')
        owner, repo = full_name.split('/')
        default_branch = resp_data.get('default_branch')
        item = GitItem()
        item['item_type'] = account_type
        item['title'] = resp_data.get('name')
        item['description'] = resp_data.get('description')
        item['site_url'] = resp_data.get('html_url')
        item['stars'] = resp_data.get('stargazers_count')
        item['forks'] = resp_data.get('forks_count')
        item['watching'] = resp_data.get('watchers_count')
        if account:
            url = 'https://api.github.com/users/{}/starred?per_page=1'.format(owner)
            yield scrapy.Request(url=url, callback=self.parse_account_starred, meta={'item': item, 'owner': owner})
        else:
            self.logger.info('Link type: {}, title: {}, desc: {}, url: {}, *: {}, fork: {}, watch: {},'.format(
                account_type, *item.values()))
            url = 'https://api.github.com/repos/{}/{}/commits'.format(owner, repo)
            yield scrapy.Request(url=url, callback=self.parse_last_commit, meta={'item': item,
                                                                                 'owner': owner,
                                                                                 'repo': repo,
                                                                                 'default_branch': default_branch})

    def parse_last_commit(self, response, **kwargs):
        item = response.meta.get('item')
        owner = response.meta.get('owner')
        repo = response.meta.get('repo')
        default_branch = response.meta.get('default_branch')
        resp_data = response.json()
        last_commit = resp_data[0]
        if response.headers.get('Link'):
            page_url = response.headers.get('Link').decode().split(',')[1].split(';')[0].split('<')[1].split('>')[0]
            yield scrapy.Request(url=page_url, callback=self.parse_first_commit,
                                 meta={'item': item, 'owner': owner, 'repo': repo, 'default_branch': default_branch,
                                       'last_commit': last_commit})
        else:
            first_commit_hash = resp_data[-1]['sha']
            url = 'https://api.github.com/repos/{}/{}/compare/{}...{}'.format(owner, repo, first_commit_hash,
                                                                              default_branch)
            yield scrapy.Request(url=url, callback=self.parse_all_commits_count, meta={'item': item,
                                                                                       'owner': owner,
                                                                                       'repo': repo,
                                                                                       'default_branch': default_branch,
                                                                                       'last_commit': last_commit})

    def parse_first_commit(self, response, **kwargs):
        item = response.meta.get('item')
        owner = response.meta.get('owner')
        repo = response.meta.get('repo')
        default_branch = response.meta.get('default_branch')
        last_commit = response.meta.get('last_commit')
        resp_data = response.json()
        first_commit_hash = resp_data[-1]['sha']
        url = 'https://api.github.com/repos/{}/{}/compare/{}...{}'.format(owner, repo, first_commit_hash,
                                                                          default_branch)
        yield scrapy.Request(url=url, callback=self.parse_all_commits_count, meta={'item': item,
                                                                                   'owner': owner,
                                                                                   'repo': repo,
                                                                                   'default_branch': default_branch,
                                                                                   'last_commit': last_commit})

    def parse_account_starred(self, response, **kwargs):
        item = response.meta.get('item')
        owner = response.meta.get('owner')
        resp_data = response.json()
        if len(resp_data):
            if response.headers.get('Link'):
                last_page_url = response.headers.get(
                    'Link').decode().split(',')[1].split(';')[0].split('<')[1].split('>')[0]
                account_stars_count = int(last_page_url.split('&page=')[1])
            else:
                account_stars_count = 0
        else:
            account_stars_count = 0
        item['stars'] = account_stars_count
        yield item

    def parse_all_commits_count(self, response, **kwargs):
        item = response.meta.get('item')
        owner = response.meta.get('owner')
        repo = response.meta.get('repo')
        default_branch = response.meta.get('default_branch')
        last_commit = response.meta.get('last_commit')
        resp_data = response.json()
        all_commits_count = resp_data.get('total_commits') + 1
        item['commits'] = all_commits_count
        item['last_commit_author'] = last_commit.get('commit', dict()).get('author', dict()).get('name')
        item['last_commit_message'] = last_commit.get('commit', dict()).get('message')
        item['last_commit_datetime'] = last_commit.get('commit', dict()).get('author', dict()).get('date')
        # ToDo: get releases count, get last release info
        item['releases'] = 0
        item['last_release_ver'] = None
        item['last_release_change_log'] = None
        item['last_release_datetime'] = None
        self.logger.info('last commit: {}'.format(last_commit))
        yield item
