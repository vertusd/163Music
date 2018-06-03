# -*- coding: utf-8 -*-
import requests
import urllib2
import logging
from bs4 import BeautifulSoup
import sys
reload(sys)

def get_new_proxies(http_proxies):
    print "new"
    xici_urls = [
        "http://www.xicidaili.com/nn/1",
        "http://www.xicidaili.com/nn/2",
        "http://www.xicidaili.com/nn/3",
        "http://www.xicidaili.com/nn/4",
    ]


    for url in xici_urls:
        print "url:" + url
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        referer = 'http://www.zhihu.com/articles'
        headers = {"User-Agent": user_agent, 'Referer': referer}
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request)
        soup = BeautifulSoup(response.read(), "lxml")
        table = soup.find("table", attrs={"id": "ip_list"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[1].text
            port = tds[2].text
            desc = tds[4].text
            if desc.encode('utf-8') == "高匿":
                proxy = "http://" + ip + ":" + port
                print "fetch" + proxy
                # noinspection PyBroadException
                try:
                    response = requests.get("http://www.baidu.com/js/bdsug.js?v=1.0.3.0", timeout=1, allow_redirects=False, proxies={"http": proxy})
                    if response.status_code == 200 and response.content.index("function") > -1:
                        http_proxies.append(proxy)
                        print "found urls" + proxy
                    else:
                        print u"找不到关键字"
                except Exception, e:
                    pass
                    #print u"验证代理IP异常：" + str(e)
                    #logging.info("验证代理IP异常：" + str(e))


if __name__ == '__main__':
    print "23"
    http_proxies = []
    get_new_proxies(http_proxies)
    print http_proxies
