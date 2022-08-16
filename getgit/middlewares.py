# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# useful for handling different item types with a single interface
from scrapy.utils.python import without_none_values


class ProxiesDownloaderMiddleware(object):

    def process_request(self, request, spider):
        if spider.ext_args.proxy:
            request.meta['proxy'] = spider.ext_args.proxy


class DefaultHeadersMiddleware:

    def __init__(self, headers):
        self._headers = headers

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.spider.ext_args.apikey:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': 'token {}'.format(crawler.spider.ext_args.apikey)
                }
        else:
            headers = without_none_values(crawler.settings['DEFAULT_REQUEST_HEADERS'])
        return cls(headers.items())

    def process_request(self, request, spider):
        for k, v in self._headers:
            request.headers.setdefault(k, v)
