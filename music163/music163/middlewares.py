# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import json
import random

import requests
import urllib2
import logging
from bs4 import BeautifulSoup
from music163.proxy_ip import *
import sys
reload(sys)
sys.setdefaultencoding("utf8")

class Music163SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RotateUserAgentMiddleware(object):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]


http_proxies = []





class ProxyMiddleware(object):

    def process_request(self, request, spider):
        if "music.163.com" in request.url:
            # 需要更换代理
            if "change_proxy" in request.meta.keys():
                logging.info("检测到需要更换代理IP的请求，change_proxy=" + str(request.meta['change_proxy']) + "，proxy=" + request.meta['proxy'])
                del request.meta['change_proxy']
                # 删除无用代理
                invalid_proxy = request.meta['proxy']
                if invalid_proxy in http_proxies:
                    http_proxies.remove(invalid_proxy)

            # 没有可用代理，需要重新从西刺代理获取
            while len(http_proxies) == 0:
                logging.info("没有可用代理，开始重新获取...")
                self.get_new_proxies()
                logging.info("本次获取到有效代理IP：" + str(http_proxies))

            proxy = random.choice(http_proxies)
            request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        if "music.163.com" in request.url:
            try:
                jsonstr = json.loads(response.body_as_unicode())
                if "msg" in jsonstr.keys():
                    if jsonstr['msg'] == 'Cheating':
                        # 请求被封则换代理重试
                        logging.info("IP被封，开始重新获取..." + request.meta['proxy'])
                        request.meta['change_proxy'] = True
                        request.dont_filter = True
                        return request
            except Exception:
                pass

        return response
    def get_new_proxies(self):
        print "get_new proxies"
        a = Proxies()
        a.verify_proxies()
        print(a.proxies)
        http_proxies = a.proxies

    def process_exception(self, request, exception, spider):
        if "music.163.com" in request.url:

            logging.error("爬取网易云音乐异常，url=" + str(request.url) + "，异常：" + str(exception) + ":"　request.meta['proxy']) 
            # 从日志看异常也是IP被封，因此换IP重新处理
            request.meta['change_proxy'] = True
            request.dont_filter = True
            import time
            time.sleep(10)
            return request

