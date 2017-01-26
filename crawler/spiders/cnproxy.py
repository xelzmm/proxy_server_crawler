from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class CnProxySpider(Spider):
    name = "cnproxy"
    allowed_domains = ["cn-proxy.com"]
    start_urls = [
        "http://cn-proxy.com/",
        "http://cn-proxy.com/archives/218"
    ]
    referer = "http://cn-proxy.com/"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('//table[@class="sortable"]/tbody/tr')
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip.xpath('td[1]/text()').extract()[0]
            item['port'] = ip.xpath('td[2]/text()').extract()[0]
            item['type'] = 'http'
            yield item
