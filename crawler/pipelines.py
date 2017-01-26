# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import json
import socket
import exceptions
import httplib
import time
from scrapy.exceptions import DropItem
from crawler.items import *
from threading import Thread
from scrapy.conf import settings
import logging
# import redis
import Queue
import gzip
from StringIO import StringIO

socket.setdefaulttimeout(2)
localhost = settings.get('LOCAL_IP')
nessus = settings.get('NESSUS')
logger = logging.getLogger('crawler.proxy.checker')
proxy_headers = [
	'x-proxy-id',
	'via',
	'x-via',
	'x-forwarded-for',
	'forwarded-for',
	'x-client-ip',
	'client-ip',
	'x-real-ip',
	'real-ip',
	'proxy-client-ip',
	'wl-proxy-client-ip',
	'x-bluecoat-via',
	'x-cc-connectivity',
	'x-mato-param',
	'x-forwarded-host',
	'x-forwarded-server'
]

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class PrintPipeline(object):
	def process_item(self, item, spider):
		if isinstance(item, ProxyIPItem):
			logger.info('\033[33m[crawled]\033[m ip: \033[33m%-15s\033[m, port: \033[33m%-5s\033[m, type: \033[33m%s\033[m' % (item['ip'], item['port'], item['type']))
			return item

class ProxyScanPipeline(object):

	def __init__(self):
		# self.redis = redis.Redis(settings.get("REDIS_IP"), settings.get("REDIS_PORT"))
		logger.info("local ip address: %s" % localhost)
		self.queue = Queue.Queue()

	def open_spider(self, spider):
		logger.info("spider opened.")
		self.running = True
		for i in xrange(100):
			thread = Thread(target=self.scan_task, args=())
			thread.start()

	def close_spider(self, spider):
		self.running = False

	def process_item(self, item, spider):
		self.queue.put(item)
		return item

	def push_to_nessus(self, item):
		pass
		# self.redis.zadd("nessus-proxy-high", "%s:%s" % (item['ip'], item['port']), item['speed'])
		# try:
		# 	# pass
		# 	urllib2.urlopen("%s?ip=%s&port=%s&speed=%s&post=%s&ssl=%s" % (nessus, item['ip'], item['port'], item['speed'], item['post'], item['ssl']))
		# except Exception, e:
		# 	print "push error", e
		# 	pass

	def scan_task(self):
		while self.running or not self.queue.empty():
			try:
				item = self.queue.get(True, 5)
				scan(item, self.push_to_nessus)
			except Queue.Empty:
				pass

def scan(item, callback=None):
	# logger.info('\033[33m[   scan]\033[m ip: \033[33m%-15s\033[m, port: \033[33m%-5s\033[m, type: \033[33m%s\033[m' % (item['ip'], item['port'], item['type']))
	result = test_proxy(item)
	if result is not None:
		logger.info('\033[32m[ result]\033[m ip: \033[32m%-15s\033[m, port: \033[32m%-5s\033[m, speed: \033[32m%-4s\033[m, type: \033[32m%s\033[m' % (item['ip'], item['port'], item['speed'], item['type']))
		if item['type'] in ['high', 'anonymous'] and test_http(item) is not None and item['speed'] < 2000:
			logger.info('\033[36m[  proxy]\033[m ip: \033[36m%-15s\033[m, port: \033[36m%-5s\033[m, speed: \033[36m%-4s\033[m, type: \033[36m%-11s\033[m, post: \033[36m%-5s\033[m, ssl: \033[36m%-5s\033[m' % (item['ip'], item['port'], item['speed'], item['type'], item['post'], item['ssl']))
			if callback is not None:
				callback(item)
	else:
		logger.info('\033[31m[ result]\033[m ip: \033[31m%-15s\033[m, port: \033[31m%-5s\033[m, type: \033[31m%s\033[m, \033[31mproxy server not alive or healthy.\033[m' % (item['ip'], item['port'], item['type']))

def test_http(item, verbose=False):
	proxyHandler = urllib2.ProxyHandler({'http':'http://%s:%s' % (item['ip'], item['port']), 'https':'http://%s:%s' % (item['ip'], item['port'])})  
	opener = urllib2.build_opener(proxyHandler)
	opener.addheaders = {
		'Accept-Encoding': 'gzip,deflate,sdch',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'User-Agent': 'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Cache-Control': 'max-age=0'
	}.items()
	check_map = {
		"http://zhidao.baidu.com/robots.txt": "Baiduspider",
		"http://weibo.com/robots.txt": "sitemap",
		"http://www.qq.com/robots.txt": "Disallow",
		"http://xyq.163.com/robots.txt": "sitemap",
		"http://www.cnbeta.com/robots.txt": "manager",
		"http://www.zhihu.com/robots.txt": "resetpassword",
		"http://www.iqiyi.com/robots.txt": "Disallow",
		"http://www.taobao.com/robots.txt": "User-agent",
		"http://www.jd.com/robots.txt": "EtaoSpider",
		"http://www.58.com/robots.txt": "User-agent"
	}
	bad = 0
	total_time = item['speed']
	success = 1
	for url in check_map:
		try: 
			req = urllib2.Request(url)
			begin = time.time()
			resp = opener.open(req)
			content = resp.read()
			if resp.info().get('Content-Encoding') == 'gzip':
				buf = StringIO(content)
				f = gzip.GzipFile(fileobj=buf)
				content = f.read()
			if content.find(check_map[url]) < 0:
				bad += 1
				if verbose:
					log.msg(repr(content), log.DEBUG)
			else:
				success += 1
				total_time += int((time.time() - begin) * 1000)
				if verbose:
					log.msg("%s %d" % (url, int((time.time() - begin) * 1000)), log.DEBUG)
		except Exception, e:
			bad += 1
			if verbose:
				logger.error("%s %s" % (url, e))
	if success * 1.0 / (len(check_map.items()) + 1) < 0.8:
		return None
	else:
		item['speed'] = total_time / success
		item['post'] = False
		try:
			req = urllib2.Request('http://httpbin.org/post', 'q=this_is_a_test')
			resp = opener.open(req)
			content = resp.read()
			if content.find('this_is_a_test') > 0:
				item['post'] = True
		except:
			pass
		item['ssl'] = False
		try:
			req = urllib2.Request('https://httpbin.org/get?q=this_is_a_test')
			resp = opener.open(req)
			content = resp.read()
			if content.find('this_is_a_test') > 0:
				item['ssl'] = True
		except:
			pass
		return item

def test_proxy(item):
	try:
		item['port'] = int(item['port'])
	except ValueError:
		return None
	if item['type'] == 'http':
		proxyHandler = urllib2.ProxyHandler({'http':'http://%s:%s' % (item['ip'], item['port']), 'https':'http://%s:%s' % (item['ip'], item['port'])})  
		opener = urllib2.build_opener(proxyHandler)
		opener.addheaders = {
			'Accept-Encoding': 'gzip',
			'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
			'User-Agent': 'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Cache-Control': 'max-age=0'
		}.items()
		try:
			req = urllib2.Request('http://httpbin.org/get')
			begin = time.time()
			resp = opener.open(req)
			content = resp.read()
			item['speed'] = int((time.time() - begin) * 1000)
			content = json.loads(content)
			if content['origin'].find(localhost) != -1:
				# print '\t[Leak Header] X-Forwarded-For: %s' % content['origin']
				item['type'] = 'transparent'
				return item
			if len(content['origin'].split(',')) > 1:
				# print '\t[Leak Header] X-Forwarded-For: %s' % content['origin']
				item['type'] = 'anonymous'
				return item
			# logger.error('ip: %s' % item['ip'])
			# for key in content['headers']:
			# 	logger.error('%s: %s' % (key, content['headers'][key]))
			for key in content['headers']:
				if content['headers'][key].find(localhost) != -1:
					# print '\t[Leak Header] %s: %s' % (key, content['headers'][key])
					item['type'] = 'transparent'
					return item
				if key.lower() in proxy_headers:
					# print '\t[Leak Header] %s: %s' % (key, content['headers'][key])
					item['type'] = 'anonymous'
			if item['type'] == 'http':
				item['type'] = 'high'
			return item
		except exceptions.ValueError, error:
			# print 'host seems to be a proxy with limitation'
			# print error
			pass
		except httplib.BadStatusLine, error:
			# print error
			pass
		except urllib2.URLError, error:
			# print error
			pass
		except socket.timeout, error:
			# print error
			pass
		except socket.error, error:
			# print error
			pass
	elif item['type'] == 'socks4':
		sock = socket.socket()
		try:
			begin = time.time()
			sock.connect((item['ip'], int(item['port'])))
			sock.send('\x04\x01\x00\x50\x36\xaf\xde\xf6MOZ\x00')
			response = sock.recv(10)
			# print repr(response) 
			if response.find('\x00\x5A') == 0:
				item['speed'] = int((time.time() - begin) * 1000)
				sock.close()
				return item
		except socket.timeout, error:
			# print error
			pass
		except socket.error, error:
			# print error
			pass
	elif item['type'] == 'socks5':
		sock = socket.socket()
		try:
			begin = time.time()
			sock.connect((item['ip'], int(item['port'])))
			sock.send('\x05\x01\x00')
			response = sock.recv(3)
			# print repr(response) 
			if response.find('\x05\x00') == 0:
				item['speed'] = int((time.time() - begin) * 1000)
				sock.close()
				return item
		except socket.timeout, error:
			# print error
			pass
		except socket.error, error:
			# print error
			pass
	return None
	# raise DropItem('proxy server not alive or healthy.')


if __name__ == '__main__':
	item = {}
	item['ip'] = '120.52.72.58'
	item['port'] = '80'
	item['speed'] = 1000
	item['type'] = 'anonymous'
	print test_http(item, True)
