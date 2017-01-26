from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class ChunzhenSpider(Spider):
    name = "chunzhen"
    allowed_domains = ["cz88.net"]
    start_urls = [
        "http://www.cz88.net/proxy/index.shtml",
        "http://www.cz88.net/proxy/http_2.shtml",
        "http://www.cz88.net/proxy/http_3.shtml",
        "http://www.cz88.net/proxy/http_4.shtml",
        "http://www.cz88.net/proxy/http_5.shtml",
        "http://www.cz88.net/proxy/http_6.shtml",
        "http://www.cz88.net/proxy/http_7.shtml",
        "http://www.cz88.net/proxy/http_8.shtml",
        "http://www.cz88.net/proxy/http_9.shtml",
        "http://www.cz88.net/proxy/http_10.shtml",
        "http://www.cz88.net/proxy/socks4.shtml",
        "http://www.cz88.net/proxy/socks4_2.shtml",
        "http://www.cz88.net/proxy/socks4_3.shtml",
        "http://www.cz88.net/proxy/socks5.shtml",
        "http://www.cz88.net/proxy/socks5_2.shtml"
    ]
    referer = 'http://www.cz88.net/proxy/index.shtml'

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        ip_list = response.xpath('//div[@id="boxright"]/div/ul/li')
        if len(ip_list) > 0:
            ip_list.pop(0)
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip.xpath('div[@class="ip"]/text()').extract()[0]
            item['port'] = ip.xpath('div[@class="port"]/text()').extract()[0]
            if response.url.find('socks4') != -1:
                item['type'] = 'socks4'
            elif response.url.find('socks5') != -1:
                item['type'] = 'socks5'
            else:
                item['type'] = 'http'
            yield item
