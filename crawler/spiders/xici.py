from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class XiciSpider(Spider):
    name = "xici"
    allowed_domains = ["xicidaili.com"]
    start_urls = [
        "http://www.xicidaili.com/nn",
        "http://www.xicidaili.com/nn/2",
        "http://www.xicidaili.com/nn/3",
        "http://www.xicidaili.com/nn/4",
        "http://www.xicidaili.com/nn/5",
        "http://www.xicidaili.com/nn/6",
        "http://www.xicidaili.com/nn/7",
        "http://www.xicidaili.com/nn/8",
        "http://www.xicidaili.com/nn/9",
        "http://www.xicidaili.com/nn/10"
    ]
    referer = 'http://www.xicidaili.com/nn'

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('//table[@id="ip_list"]/tr')
        if len(ip_list) > 0:
            ip_list.pop(0)
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip.xpath('td[2]/text()').extract()[0]
            item['port'] = ip.xpath('td[3]/text()').extract()[0]
            item['type'] = 'http'
            yield item
