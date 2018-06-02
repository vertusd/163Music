# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request, FormRequest
from ..settings import DEFAULT_REQUEST_HEADERS
from ..items import MusicItem
import re
import json
import requests
from urllib import parse


class MusicSpider(Spider):
    name = "music"
    allowed_domains = ["163.com"]
    base_url = 'https://music.163.com'
    # ids = ['1001','1002','1003','2001','2002','2003','6001','6002','6003','7001','7002','7003','4001','4002','4003']
    cats = [u'民谣', u'流行', u'摇滚', u'民谣', u'电子', u'舞曲', u'说唱', u'轻音乐', u'爵士', u'乡村', u'R&B/Soul', u'古典', u'民族', u'英伦', u'金属', u'朋克', u'蓝调', u'雷鬼', u'世界音乐', u'拉丁', u'另类/独立', u'New Age', u'古风', u'后摇', u'Bossa Nova']
    # initials = [i for i in range(65, 91)]+[0]
    # offsets = [i*35 for i in range(0,37)]
    
    
    def start_requests(self):
        for cat in self.cats: 
            catDict = {'cat': cat.encode('utf8')}
            url = self.base_url+'/discover/playlist/?{cat}'.format(cat=parse.urlencode(catDict))
            yield Request(url, meta={'cat': cat}, callback=self.getSheetPageNum)

    #获取该分类下歌单页面总数再按页抓取  
    def getSheetPageNum(self, response):
        list=response.xpath('//*[@id="m-pl-pager"]/div/a[@class="zpgi"]')
        cat=response.meta['cat']
        sheetPageNum=int(list[-1].re('<a.*>(\d*?)</a>')[0])
        # print("========cat:"+str(cat)+" sheetPageNum:"+str(sheetPageNum))
        #35条/歌单页面
        offsets = [i*35 for i in range(0,sheetPageNum)]
        for offset in offsets:
                catDict = {'cat': cat.encode('utf8')}
                url = '{url}/discover/playlist/?order=hot&{cat}&limit=35&offset={offset}'.format(url=self.base_url, cat=parse.urlencode(catDict), offset=offset)
                yield Request(url, meta={'cat': cat}, callback=self.parse_sheet_list)

    # 获得页面所有歌单的id
    def parse_sheet_list(self, response):        
         for line in response.xpath('//*[@id="m-pl-container"]/li/p[@class="dec"]/*'): 
            sheetId=line.re('href\=\"\/playlist\?id\=(\d*?)\"')[0]
            # sheetName=line.re('<a title=\"(.*?)\"')[0]
            sheetUrl=self.base_url + "/playlist?id=" + sheetId
            yield Request(sheetUrl, meta={'cat': response.meta['cat']}, callback=self.parse_sheet)     

    # 获取歌单所有的歌曲id 
    def parse_sheet(self,response): 
        musics = response.xpath('//ul[@class="f-hide"]/li/a/@href').extract()
        for music in musics:
            music_id = music[9:]
            music_url = self.base_url + music
            yield Request(music_url, meta={'id': music_id, 'cat': response.meta['cat']}, callback=self.parse_music)

    # 获得音乐信息
    def parse_music(self, response):
        music_id = response.meta['id']
        music = response.xpath('//div[@class="tit"]/em[@class="f-ff2"]/text()').extract_first()
        artistName = response.xpath('//div[@class="cnt"]/p[1]/span/a/text()').extract_first()
        artistId = response.xpath('//div[@class="cnt"]/p[1]/span/*')[0].re('href\=\"\/artist\?id\=(\d*?)\"')[0]
        albumName = response.xpath('//div[@class="cnt"]/p[2]/a/text()').extract_first()
        albumId = response.xpath('//div[@class="cnt"]/p[2]/*')[0].re('href\=\"\/album\?id\=(\d*?)\"')[0]
        artistInfo = {"artistId": artistId, "artistName": artistName}
        albumInfo = {"albumName": albumName, "albumID": albumId}
        data = {
            'csrf_token': '',
            'params': 'Ak2s0LoP1GRJYqE3XxJUZVYK9uPEXSTttmAS+8uVLnYRoUt/Xgqdrt/13nr6OYhi75QSTlQ9FcZaWElIwE+oz9qXAu87t2DHj6Auu+2yBJDr+arG+irBbjIvKJGfjgBac+kSm2ePwf4rfuHSKVgQu1cYMdqFVnB+ojBsWopHcexbvLylDIMPulPljAWK6MR8',
            'encSecKey': '8c85d1b6f53bfebaf5258d171f3526c06980cbcaf490d759eac82145ee27198297c152dd95e7ea0f08cfb7281588cdab305946e01b9d84f0b49700f9c2eb6eeced8624b16ce378bccd24341b1b5ad3d84ebd707dbbd18a4f01c2a007cd47de32f28ca395c9715afa134ed9ee321caa7f28ec82b94307d75144f6b5b134a9ce1a'
        }
        DEFAULT_REQUEST_HEADERS['Referer'] = self.base_url + '/playlist?id=' + str(music_id)
        music_comment = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(music_id)
        yield FormRequest(music_comment, meta={'id':music_id,'music':music,'artistInfo':artistInfo,'albumInfo':albumInfo, 'cat': response.meta['cat']}, \
                          callback=self.parse_comment, formdata=data)

    # 获得音乐的精彩评论
    def parse_comment(self, response):
        id = response.meta['id']
        result = json.loads(response.text)
        music = response.meta['music']
        artistInfo = response.meta['artistInfo']
        category = response.meta['cat']
        albumInfo = response.meta['albumInfo']
        lyrics = self.getLyricsById(id)
        commentNum = result.get('total')
        comments = []
        if 'hotComments' in result.keys():
            for comment in result.get('hotComments'):
                hotcomment_author = comment['user']['nickname']
                hotcomment = comment['content']
                hotcomment_like = comment['likedCount']
                hotcomment_avatar = comment['user']['avatarUrl']
                data = {
                    'nickname': hotcomment_author,
                    'content': hotcomment,
                    'likedcount': hotcomment_like,
                    'avatarurl': hotcomment_avatar
                }
                comments.append(data)

        item = MusicItem()
        for field in item.fields:
            try:
                item[field] = eval(field)
            except:
                print('Field is not defined', field)
        # print("********* category:"+category)
        yield item

    #获取歌词
    def getLyricsById(self,songId):
        url="http://music.163.com/api/song/media?id="+songId
        headers = {
            'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://music.163.com'
        }
        r = requests.get(url=url, headers=headers).json()
        if 'lyric' in r:
            return r['lyric']
        else:
            return '无歌词'
