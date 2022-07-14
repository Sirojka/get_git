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
        # 'LOG_FILE': '/var/log/getgit_log.log',
        'LOG_LEVEL': 'INFO'
    }

    test_links = [
        'https://github.com/ronggang',
        # 'https://github.com/arm-software',
        'https://github.com/scrapy/scrapy',
        'https://github.com/scrapy'
        ]

    def __init__(self, ext_args):
        self.ext_args = ext_args
        super().__init__()

    def check_link(self, link):
        api_url = None
        parsed_url = urlparse(url=link)
        if parsed_url.netloc == 'github.com':
            url_path = parsed_url.path.strip('/').lstrip('/')
            url_path_chunks = url_path.split('/')
            if len(url_path_chunks) == 1:
                api_url = 'https://api.github.com/users/{}/repos'.format(url_path_chunks[0])
            else:
                self.logger.error('Bad link: {}, not an account link, maybe direct repo link'.format(link))
        else:
            self.logger.error('Bad link: {}, not a github site'.format(link))
        return api_url

    def start_requests(self):
        self.logger.info('Spider version: {}'.format(self.settings.get('VERSION')))
        self.logger.info(self.crawler.stats.get_stats())
        if self.ext_args.test:
            self.links = self.test_links
            self.logger.warning('Running in TEST MODE!!! Will use test list of links, {} items.'.format(
                len(self.links)))
        for link in self.links:
            url = self.check_link(link=link)
            if url:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        resp_data = response.json()
        owner = None
        if len(resp_data) > 0:
            for repo in resp_data:
                item = GitItem()
                item['full_name'] = repo.get('full_name')
                self.logger.info('Repo: {}'.format(item['full_name']))
                item['description'] = repo.get('description')
                item['site_url'] = repo.get('html_url')
                item['stars'] = repo.get('stargazers_count')
                item['forks'] = repo.get('forks_count')
                item['watching'] = repo.get('watchers_count')
                owner = repo.get('owner', dict()).get('login')
                default_branch = repo.get('default_branch')
                url = 'https://api.github.com/repos/{}/commits'.format(item['full_name'])
                yield scrapy.Request(url=url, callback=self.parse_last_commit, meta={'item': item,
                                                                                     'default_branch': default_branch})
        if response.headers.get('Link'):
            nav = response.headers.get('Link').decode().split(',')
            for n in nav:
                if 'next' in n:
                    next_page_url = n.split(';')[0].split('<')[1].split('>')[0]
                    next_page_num = int(next_page_url.split('=')[1])
                    url = 'https://api.github.com/users/{}/repos?page={}'.format(owner, next_page_num)
                    yield scrapy.Request(url=url, callback=self.parse)

    def parse_last_commit(self, response, **kwargs):
        item = response.meta.get('item')
        default_branch = response.meta.get('default_branch')
        owner, repo = item.get('full_name').split('/')
        resp_data = response.json()
        last_commit = resp_data[0]
        if response.headers.get('Link'):
            page_url = response.headers.get('Link').decode().split(',')[1].split(';')[0].split('<')[1].split('>')[0]
            yield scrapy.Request(url=page_url, callback=self.parse_first_commit,
                                 meta={'item': item, 'default_branch': default_branch, 'last_commit': last_commit})
        else:
            first_commit_hash = resp_data[-1]['sha']
            url = 'https://api.github.com/repos/{}/{}/compare/{}...{}'.format(owner, repo, first_commit_hash,
                                                                              default_branch)
            yield scrapy.Request(url=url, callback=self.parse_all_commits_count, meta={'item': item,
                                                                                       'default_branch': default_branch,
                                                                                       'last_commit': last_commit})

    def parse_first_commit(self, response, **kwargs):
        item = response.meta.get('item')
        default_branch = response.meta.get('default_branch')
        last_commit = response.meta.get('last_commit')
        owner, repo = item.get('full_name').split('/')
        resp_data = response.json()
        first_commit_hash = resp_data[-1]['sha']
        url = 'https://api.github.com/repos/{}/{}/compare/{}...{}'.format(owner, repo, first_commit_hash,
                                                                          default_branch)
        yield scrapy.Request(url=url, callback=self.parse_all_commits_count, meta={'item': item,
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
        last_commit = response.meta.get('last_commit')
        owner, repo = item.get('full_name').split('/')
        resp_data = response.json()
        all_commits_count = resp_data.get('total_commits') + 1
        item['commits'] = all_commits_count
        item['last_commit_author'] = last_commit.get('commit', dict()).get('author', dict()).get('name')
        item['last_commit_message'] = last_commit.get('commit', dict()).get('message')
        item['last_commit_datetime'] = last_commit.get('commit', dict()).get('author', dict()).get('date')
        url = 'https://api.github.com/repos/{}/{}/releases?per_page=1'.format(owner, repo)
        yield scrapy.Request(url=url, callback=self.parse_all_releases, meta={'item': item})

    def parse_all_releases(self, response, **kwargs):
        item = response.meta.get('item')
        resp_data = response.json()
        if len(resp_data):
            last_release = resp_data[0]
            if response.headers.get('Link'):
                last_page_url = response.headers.get(
                    'Link').decode().split(',')[1].split(';')[0].split('<')[1].split('>')[0]
                all_releases_count = int(last_page_url.split('&page=')[1])
            else:
                all_releases_count = 0
        else:
            all_releases_count = 0
            last_release = dict()
        item['releases'] = all_releases_count
        item['last_release_ver'] = last_release.get('name')
        item['last_release_change_log'] = last_release.get('body')
        item['last_release_datetime'] = last_release.get('published_at')
        yield item
