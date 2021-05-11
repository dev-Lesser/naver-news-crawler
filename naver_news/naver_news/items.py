# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NaverNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    title = scrapy.Field() # 뉴스 타이틀
    url = scrapy.Field() # 뉴스 url
    contents = scrapy.Field() # 뉴스 본문
    press = scrapy.Field() # 언론사
    datetime = scrapy.Field() # 기사작성시간
