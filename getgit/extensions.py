from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import NotConfigured


class SpiderLinksLoader:

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        # crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        datafile = spider.ext_args.datafile
        if datafile:
            spider.logger.info('Datafile selected, links will be loaded from file: {}'.format(datafile))
            try:
                with open(datafile, 'r') as text_file:
                    spider.links = [line.strip() for line in text_file.readlines()]
            except Exception as e:
                spider.links = list()
                spider.logger.error('{}, file: {}'.format(e, datafile))
        else:
            spider.links = list()
            spider.logger.warning('No datafile selected, using test list of links'.format())
        spider.logger.info('Links loaded: {}.'.format(len(spider.links)))
