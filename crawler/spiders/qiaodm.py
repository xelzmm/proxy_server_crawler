from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from crawler.items import ProxyIPItem

class QiaodmSpider(Spider):
    name = "qiaodm"
    allowed_domains = ["qiaodm.com"]
    start_urls = [
        "http://ip.qiaodm.com/",
        "http://ip.qiaodm.com/free/index.html"
    ]
    referer = "http://ip.qiaodm.com/"

    def start_requests(self):
        for item in self.start_urls:
            yield Request(url=item, headers={'Referer': self.referer}, dont_filter=True)

    def parse(self, response):
        # pages = response.xpath('//*[@id="flip"]/div/span | //*[@id="flip"]/div/a')
        # if len(pages) > 4:
        #     next_page = pages[-2].xpath('@href').extract()
        #     if len(next_page) == 1:
        #         yield Request(url='%s/%s' % (self.referer, next_page[0]), headers={'Referer': response.url})
        if response.request.url == 'http://ip.qiaodm.com/free/index.html':
            hot_urls = response.xpath('//div[@class="freeb"]/a[contains(@href,"free")]/@href').extract()
            for url in hot_urls:
                yield Request(url=url, headers={'Referer': self.referer})
            country_urls = response.xpath('//a[@class="item"]/@href').extract()
            for url in country_urls:
                yield Request(url=url, headers={'Referer': self.referer})

        ip_list = response.xpath('//*[@id="main_container"]/div[1]/table/tbody/tr')
        if len(ip_list) > 2:
            ip_list.pop(1)
            ip_list.pop(0)
        for line in ip_list:
            item = ProxyIPItem()
            columns = line.xpath('td')
            ip_spans = columns[0].xpath('node()/script/text() | node()[not(contains(@style, "none"))]/text()').extract()
            item['ip'] = ''.join([a.replace('document.write(\'','').replace('\');','') for a in ip_spans])
            # port = columns[1].xpath('text()').extract()[0]
            port = columns[1].xpath('@class').extract()[0].split(' ')[1]
            port = int(''.join([str("ABCDEFGHIZ".index(c)) for c in port])) / 8
            item['port'] = port
            # port = columns[1].xpath('script/text()').extract()[0]
            # port = port[port.index('=') + 1:port.index(';')]
            # item['port'] = ''.join([str(eval(a)) for a in port.split('+')])
            item['type'] = 'http'
            yield item
