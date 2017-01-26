from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

from urllib import unquote
from re import search

class ProxylistsSpider(Spider):
    name = "proxylists"
    allowed_domains = ["proxylists.net"]
    start_urls = [
        "http://www.proxylists.net/cn_1_ext.html",
    ]
    referer = "http://www.proxylists.net/"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('body/font/b/table/tr[1]/td[2]/table/tr')
        if len(ip_list) > 3:
            ip_list.pop(1)
            ip_list.pop(0)
            ip = ip_list.pop()
            cur_page = int(search('cn_(\d+)_ext', response.url).group(1))
            total = len(ip.xpath('td/b/a'))
            if total - cur_page > 1:
                yield Request(url="http://www.proxylists.net/cn_%d_ext.html" % (cur_page + 1), headers={'Referer': response.url})
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = unquote(search('%22(.*)%22', ip.xpath('td/script/text()').extract()[0]).group(1))
            item['port'] = ip.xpath('td[2]/text()').extract()[0]
            type = ip.xpath('td[3]/text()').extract()[0].lower()
            type = 'http' if type in ['anonymous', 'transparent', 'high anonymity', 'distorting'] else type
            item['type'] = type
            yield item

