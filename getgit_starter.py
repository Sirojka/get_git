#!/usr/bin/python3
# -*- coding: utf-8 -*-
# coding: utf8

"""
Copyright: (c) 2022, Siarhei Straltsou
init release 2022-07-12
https://github.com scraper - the program for scraping info about GitHub account/repo using api/html
"""

import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from getgit.spiders.gitcrawler import GitSpider


if __name__ == "__main__":
    p_settings = get_project_settings()
    datafile = p_settings.get('LINKS_FILE_NAME')
    parser = argparse.ArgumentParser(description='github.com scraper', add_help=True)
    parser.add_argument('--test', action='store_true', dest='test', default=False,
                        help='test mode: for simple test with the few accounts as argument')
    # ToDo: use this arg to switch api/html mode
    parser.add_argument('--api', action='store_true', dest='api', default=False,
                        help='use api or dumb html scraper mode')
    parser.add_argument('--datafile', action='store', dest='datafile', type=str, default=datafile,
                        help='path to the data file with list of links to repo/projects')
    parser.add_argument('--mongo_uri', action='store', dest='mongo_uri', type=str, default='mongodb://localhost:27017',
                        help='mongo db uri for connect to mongo db database, mongodb://HOST:POST')
    parser.add_argument('--proxy', action='store', dest='proxy', type=str, default='',
                        help='enable proxy with provided connection string in format http://USER:PASS@HOST:PORT')
    args = parser.parse_args()
    process = CrawlerProcess(p_settings)
    process.crawl(GitSpider, ext_args=args)
    process.start()
