from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

from re import search

class XroxySpider(Spider):
    name = "xroxy"
    allowed_domains = ["xroxy.com"]
    start_urls = [
        "http://www.xroxy.com/proxylist.php",
    ]
    referer = "http://www.xroxy.com/"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer})

    def parse(self, response):
        total = int(response.xpath('//*[@id="content"]/table[2]/tr/td[1]/table/tr[2]/td/small/b/text()').extract()[0]) / 10
        if response.url.find('pnum=') == -1:
            cur_page = 0
        else:
            cur_page = int(search('pnum=(\d+)', response.url).group(1))
        if total - cur_page > 1:
            yield Request(url="http://www.xroxy.com/proxylist.php?pnum=%d" % (cur_page + 1), headers={'Referer': response.url})
        ip_list = response.xpath('//*[@id="content"]/table[1]/tr[@class="row0"] | //*[@id="content"]/table[1]/tr[@class="row1"]')
        for ip in ip_list:
            item = ProxyIPItem()
            item['ip'] = ip.xpath('td[2]/a/text()').extract()[0].strip()
            item['port'] = ip.xpath('td[3]/a/text()').extract()[0].strip()
            type = ip.xpath('td[4]/a/text()').extract()[0].strip().lower()
            type = 'http' if type in ['anonymous', 'transparent', 'high anonymity', 'distorting'] else type
            item['type'] = type
            yield item

