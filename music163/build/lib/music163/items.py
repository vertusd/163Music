# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MusicItem(scrapy.Item):
    # define the fields for your item here like:
    table_name = 'music'
    id = scrapy.Field()
    music = scrapy.Field()
    artistInfo = scrapy.Field()
    albumInfo = scrapy.Field()
    category = scrapy.Field()
    comments = scrapy.Field()
    commentNum = scrapy.Field()
    lyrics = scrapy.Field()
