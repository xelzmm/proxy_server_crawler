##Introduction

**Proxy Server Crawler** is a tool used to crawl public proxy servers from proxy websites. When crawled a proxy server(ip::port::type), it will test the functionality of the server automatically.

Currently supported websites:

* http://www.66ip.cn
* http://www.cz88.net
* http://www.cn-proxy.com
* http://www.haodailiip.com
* http://www.kuaidaili.com
* http://www.proxylists.net
* http://www.qiaodm.net
* http://www.socks-proxy.net
* http://www.xroxy.com
* http://www.xicidaili.com

Currently supported testing(for http proxy)

* ssl support
* post support
* speed (tested with 10 frequently used sites)
* type(high/anonymous/transparent)

## Requirements

* Python >= 2.7
* Scrapy 1.3.0 (not tested for lower version)
* node (for some sites, you need node to bypass waf based on javascript)

## Usage

```bash
cd proxy_server_crawler
scrapy crawl chunzhen
```

[log]

```
[ result] ip: 59.41.214.218  , port: 3128 , type: http, proxy server not alive or healthy.
[ result] ip: 117.90.6.67    , port: 9000 , type: http, proxy server not alive or healthy.
[ result] ip: 117.175.183.10 , port: 8123 , speed: 984 , type: high
[ result] ip: 180.95.154.221 , port: 80   , type: http, proxy server not alive or healthy.
[ result] ip: 110.73.0.206   , port: 8123 , type: http, proxy server not alive or healthy.
[  proxy] ip: 124.88.67.54   , port: 80   , speed: 448 , type: high       , post: True , ssl: False
[ result] ip: 117.90.2.149   , port: 9000 , type: http, proxy server not alive or healthy.
[ result] ip: 115.212.165.170, port: 9000 , type: http, proxy server not alive or healthy.
[  proxy] ip: 118.123.22.192 , port: 3128 , speed: 769 , type: high       , post: True , ssl: False
[  proxy] ip: 117.175.183.10 , port: 8123 , speed: 908 , type: high       , post: True , ssl: True 
```

##License

The MIT License (MIT)
