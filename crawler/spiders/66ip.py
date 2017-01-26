from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem
import random
import re

from urllib import unquote
from re import search

class _66IPSpider(Spider):
    name = "66ip"
    allowed_domains = ["66ip.cn"]
    start_urls = [
        "http://www.66ip.cn/mo.php?sxb=&tqsl=%s&port=&export=&ktip=&sxa=&submit=%%CC%%E1++%%C8%%A1&textarea=" % random.randint(3000, 5000),
        "http://www.66ip.cn/nmtq.php?getnum=%s&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=71daili" % random.randint(3000, 5000)
    ]

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': item[:item.index('?')]})

    def parse(self, response):
        ip_list = re.findall("\d+\.\d+\.\d+\.\d+:\d+", response.body)
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip[:ip.index(':')]
            item['port'] = ip[ip.index(":") + 1:]
            item['type'] = 'http'
            yield item

