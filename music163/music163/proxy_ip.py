# *-* coding:utf-8 *-*
import requests
from bs4 import BeautifulSoup
import lxml
from multiprocessing import Process, Queue
import random
import json
import time
import requests
import requests
import urllib2

class Proxies(object):
    """docstring for Proxies"""

    def __init__(self, page=3):
        print "__init proxies"
        self.proxies = []
        self.verify_pro = []
        self.page_count = page
        self.get_proxies_mrhinkydink()


        #self.get_proxies()
        #self.get_proxies_nn()



    def  get_proxies_xundaili(self):
        print "get_proxies"
        page = 1
        page_stop = page + self.page_count
        print "page_stop" + str(page_stop)
        print "page_start "  + str(page)
        while page < page_stop:
            url = 'https://www.kuaidaili.com/free/inha/%d/' % page
            user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
            referer = 'https://www.kuaidaili.com/free/inha/1/'
            headers = {"User-Agent": user_agent, 'Referer': referer}
            request = urllib2.Request(url, headers=headers)
            html = urllib2.urlopen(request)
            print "fetch " + url
            #print html
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='list')
            if ip_list == None:
                print u"fail to fetch proxy"
                return 
            if type(ip_list) == "NoneType" :
                print u"fail to fetch proxy"
                return
            for odd in ip_list.find_all('tr'):
                if  odd.find_all('td'):
                    protocol = odd.find_all('td')[3].get_text().lower() + '://'
                    self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[0:2]]))
            import time 
            time.sleep(5)
            page += 1

    def  get_proxies_mrhinkydink(self):
        print "get_proxies"
        page = 1
        page_stop = page + self.page_count
        print "page_stop" + str(page_stop)
        print "page_start "  + str(page)
        while page < page_stop:
            if page == 1:
                url = 'http://www.mrhinkydink.com/proxies.htm'
            else:
                url = 'http://www.mrhinkydink.com/proxies%s.htm' % page
            
            user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
            referer = 'http://www.mrhinkydink.com/'
            headers = {"User-Agent": user_agent, 'Referer': referer}
            request = urllib2.Request(url, headers=headers)
            html = urllib2.urlopen(request)
            print "fetch " + url
            #print html
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find_all("tr", {"class": "text"})
            if ip_list == None:
                print u"fail to fetch proxy"
                return 
            if type(ip_list) == "NoneType" :
                print u"fail to fetch proxy"
                return
            #print ip_list
            for tr in ip_list:
                if tr:
                    #print tr
                    if  tr.find_all('td'):
                        self.proxies.append(("http://" + ':'.join([x.get_text() for x in tr.find_all('td')[0:2]])).replace("*","").replace("\u2020",""))
                        self.proxies.append(("https://" + ':'.join([x.get_text() for x in tr.find_all('td')[0:2]])).replace("*","").replace("\u2020",""))
            import time 
            time.sleep(2)
            page += 1
    
    def get_proxies(self):
        print "get_proxies"
        page = random.randint(1, 10)
        page_stop = page + self.page_count
        print "page_stop" + str(page_stop)
        print "page_start "  + str(page)
        while page < page_stop:
           
            url = 'http://www.xicidaili.com/nt/%d' % page
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            referer = 'http://www.zhihu.com/articles'
            headers = {"User-Agent": user_agent, 'Referer': referer}
            request = urllib2.Request(url, headers=headers)
            html = urllib2.urlopen(request)
            print "fetch" + url
            #print html
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            if ip_list == None:
                print u"fail to fetch proxy"
                return 
            if type(ip_list) == "NoneType" :
                print u"fail to fetch proxy"
                return
            for odd in ip_list.find_all(class_='odd'):
                protocol = odd.find_all('td')[5].get_text().lower() + '://'
                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
            page += 1

    def get_proxies_nn(self):
        page = random.randint(1, 10)
        page_stop = page + self.page_count
        while page < page_stop:
            url = 'http://www.xicidaili.com/nn/%d' % page
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            referer = 'http://www.zhihu.com/articles'
            headers = {"User-Agent": user_agent, 'Referer': referer}
            request = urllib2.Request(url, headers=headers)
            html = urllib2.urlopen(request)
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            if ip_list == None:
                print u"fail to fetch proxy"
                return 
            for odd in ip_list.find_all(class_='odd'):
                protocol = odd.find_all('td')[5].get_text().lower() + '://'
                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
            page += 1

    def verify_proxies(self):
        # 没验证的代理
        old_queue = Queue()
        # 验证后的代理
        new_queue = Queue()
        print('verify proxy........')
        works = []
        for _ in range(15):
            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for proxy in self.proxies:
            old_queue.put(proxy)
        for work in works:
            old_queue.put(0)
        for work in works:
            work.join()
        self.proxies = []
        while 1:
            try:
                self.proxies.append(new_queue.get(timeout=1))
            except:
                break
        print('verify_proxies done!')

    def verify_one_proxy(self, old_queue, new_queue):
        while 1:
            proxy = old_queue.get()
            if proxy == 0: break
            protocol = 'https' if 'https' in proxy else 'http'
            if u"\u0202" in proxy or r"\u2020" in proxy or u"†" in proxy:
                print('fail %s' % proxy)
                return
            proxies = {protocol: proxy}
            if "copy" in proxy:
                print('fail %s' % proxy)
                return
            try:
                    response =requests.get('http://music.163.com/#/discover/artist', proxies=proxies, timeout=1) 
                    if response.status_code== 200 and response.content.index("GWebpSupport")> -1:
                        print('success %s' % proxy)
                        new_queue.put(proxy)
            except:
                print('fail %s' % proxy)


if __name__ == '__main__':
    a = Proxies()
    a.verify_proxies()
    print(a.proxies)
    proxie = a.proxies
    with open('proxies.txt', 'a') as f:
        for proxy in proxie:
            f.write(proxy + '\n')