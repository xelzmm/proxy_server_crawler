# -*- coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class HaodailiSpider(Spider):
    name = "haodaili"
    allowed_domains = ["haodailiip.com"]
    start_urls = [
        "http://www.haodailiip.com/guonei",
        "http://www.haodailiip.com/guoji"
    ]
    referer = "http://www.haodailiip.com"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('/html/body/center/table[2]/tr/td[1]/table/tr')
        if len(ip_list) > 1:
            ip_list.pop(0)
        has_next = True
        for ip in ip_list:
            item = ProxyIPItem()
            columns = ip.xpath('td/text()').extract()
            item['ip'] = columns[0].strip()
            item['port'] = columns[1].strip()
            item['type'] = 'http'
            if columns[-1].strip() == u'超时':
                has_next = False
            yield item
        if has_next:
            url = "%s%s" % (self.referer, response.xpath('/html/body/center/table[2]/tr/td[1]/p/a[last()]/@href').extract()[0])
            yield Request(url=url, headers={'Referer': response.url})

