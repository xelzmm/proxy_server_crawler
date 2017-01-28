from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem
import re
import os

class KuaidailiSpider(Spider):
    name = "kuaidaili"
    allowed_domains = ["kuaidaili.com"]
    start_urls = [
        "http://www.kuaidaili.com"
    ]
    referer = 'http://www.kuaidaili.com'

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer}, meta={'handle_httpstatus_list': [521]}, callback=self.parseInitRequest)

    def parse(self, response):
        ip_list = response.xpath('//div[@id="index_free_list"]/table/tbody/tr')
        for line in ip_list:
            item = ProxyIPItem(type="http")
            item["ip"] = line.xpath('td[1]/text()').extract()[0].strip()
            item["port"] = line.xpath('td[2]/text()').extract()[0].strip()
            yield item
        if response.request.url.find('proxylist') < 0:
            pages = response.xpath('//div[@id="listnav"]/ul/li/a')
            pages.pop(0)
            for page in pages:
                path = page.xpath('@href').extract()[0]
                yield Request(url=self.start_urls[0] + path, headers={'Referer': response.request.url, 'User-Agent': response.request.headers.get('User-Agent')})
        

    def parseInitRequest(self, response):
        if response.status == 200:
            yield Request(url=response.request.url, headers={'Referer': self.referer, 'User-Agent': response.request.headers.get('User-Agent')}, dont_filter=True)
            return
        group = re.search('setTimeout\("\w+\((\d+)\)".*(function .*"\);})', response.body)
        key, function = group.group(1), group.group(2)
        script = '!%s(%s)' % (function.replace('=eval', '=console.log'), key)
        result = os.popen("node -e '%s'" % script).read()
        path = re.search('"(.*)"', result).group(1)
	url = response.request.url + path
        yield Request(url=url, headers={'Referer': response.request.url, 'User-Agent': response.request.headers.get('User-Agent')}, dont_filter=True)                                
