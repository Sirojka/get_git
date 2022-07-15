# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# useful for handling different item types with a single interface


class ProxiesDownloaderMiddleware(object):

    def process_request(self, request, spider):
        if spider.ext_args.proxy:
            request.meta['proxy'] = spider.ext_args.proxy
