# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ProxyIPItem(scrapy.Item):
	ip = scrapy.Field()
	port = scrapy.Field()
	type = scrapy.Field()
	speed = scrapy.Field()
	post = scrapy.Field()
	ssl = scrapy.Field()

