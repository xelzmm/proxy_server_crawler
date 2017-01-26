from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class SocksProxySpider(Spider):
    name = "socksproxy"
    allowed_domains = ["socks-proxy.net"]
    start_urls = [
        "http://www.socks-proxy.net"
    ]
    referer = "http://www.socks-proxy.net"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('//*[@id="proxylisttable"]/tbody/tr')
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip.xpath('td[1]/text()').extract()[0]
            item['port'] = ip.xpath('td[2]/text()').extract()[0]
            item['type'] = ip.xpath('td[5]/text()').extract()[0].lower()
            yield item
