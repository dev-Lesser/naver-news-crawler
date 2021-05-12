import scrapy
from lxml import html
from naver_news.items import NaverNewsItem
import pandas as pd
import re
import datetime
df = pd.read_csv('../언론사_코드_매핑.csv') # 네이버 뉴스에서 사용하고있는 언론사별 코드번호 매핑 파일 > 각 element 의 xpath 를 이용해, 자동화 함
class NavernewsSpider(scrapy.Spider):
    
    name = 'navernews'
    
    def start_requests(self):
        global df
        ## 코로나 + 백신 으로 검색, 최근 6개월간, 언론사별(언론사코드), start 1, 11 로 10개씩 페이지네이션
        ## url 구성 = query(검색키워드), startdate, enddate, sort=1(최신순) news_office_checked(언론사코드), start(pagination start id)
        ## data 수집 기간 범위를 설정합니다. 네이버 뉴스의 경우 4000개의 기사 이상으로 제공하고 있지 않기 때문에, 날짜별, 언론사별 가능한 많은 기사를 수집하는 것이 목표입니다.
        date_range = [str(pd.date_range('2020-12-01','2021-02-01', freq='1M')[i]).split()[0].split('-') for i in range(2) ] 
        for idate in range(len(date_range)-1):
            root_url = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EC%BD%94%EB%A1%9C%EB%82%98%20%EB%B0%B1%EC%8B%A0&sort=1&photo=0&field=0&pd=3&ds={ds}&de={de}&mynews=1&office_type=1&office_section_code=1&news_office_checked={press_code}&nso=so:dd,p:from{ds_t}to{de_t},a:all&start={offset}'
            start_urls = [root_url.format(press_code=i, offset=1, ds='.'.join(date_range[idate]), de='.'.join(date_range[idate+1]), ds_t=''.join(date_range[idate]), de_t=''.join(date_range[idate+1])) for i in df['코드']] # 시작 url 구축
            
            for iurl in start_urls:
                yield scrapy.Request(
                    url=iurl, 
                    callback=self.parse_url
                )
    def parse_url(self, response):
        tree = html.fromstring(response.text)
        pattern_minute = re.compile('[0-9]*[분]+\s[전]')
        pattern_hour = re.compile('[0-9]*[시간]+\s[전]')
        pattern_day = re.compile('[0-9]*[일]+\s[전]')
        pattern_date = re.compile('[0-9]+[.]+[0-9]+[.]+[0-9]+[.]+')
        date = [i for i in tree.xpath('//span[@class="info"]/text()') if pattern_day.match(i) or pattern_hour.match(i) or pattern_day.match(i) or pattern_date.match(i)]
        
        items = list(zip(*[tree.xpath('//div[@class="news_area"]/a/@title'),tree.xpath('//div[@class="news_area"]/a/@href'),tree.xpath('//a[@class="info press"]/text()'), date]))
        next_page_ = tree.xpath('//div[@class="sc_page"]/a[@class="btn_next"]/@aria-disabled')
        next_page =next_page_[0] if next_page_ != [] else 'true'
        next_url = tree.xpath('//div[@class="sc_page"]/a[@class="btn_next"]/@href')
        next_page_url = next_url[0] if next_url !=[] else False # 다음 페이지가 없을 경우, length 에러가 뜨면서 넘어감
        
        for item in items:
            if not item[1].startswith('https://zdnet.co.kr'): # error 가 뜨는 특정 사이트 제외
                yield scrapy.Request(
                    url=item[1], # url
                    callback=self.parse,
                    meta={'title':item[0],'url':item[1],'press':item[2], 'datetime':item[3]}
                )
        if next_page == 'false' : # 다음 페이지가 있을 경우
            yield scrapy.Request(
                url='https://search.naver.com/search.naver'+next_page_url,
                callback=self.parse_url,
            )
    def parse(self, response):
        news_items = NaverNewsItem()
        idatetime = response.meta['datetime']
        pattern = re.compile('[0-9]+[분|시간|일]+\s[전]+') ## 시간스탬프를 위한 정규식
        now = datetime.datetime.now()
        pattern_minute = re.compile('[0-9]*[분]+\s[전]')
        pattern_hour = re.compile('[0-9]*[시간]+\s[전]')
        pattern_day = re.compile('[0-9]*[일]+\s[전]')
        if pattern_minute.match(idatetime):
            result = pattern_minute.match(idatetime)
            minute = result.group().split('분')[0]
            idatetime = now - datetime.timedelta(minutes=int(minute))
            idatetime = idatetime.strftime('%Y.%m.%d.')
        elif pattern_hour.match(idatetime):
            result = pattern_hour.match(idatetime)
            hour = result.group().split('시간')[0]
            idatetime = now - datetime.timedelta(hours=int(hour))
            idatetime = idatetime.strftime('%Y.%m.%d.')
        elif pattern_day.match(idatetime):
            result = pattern_day.match(idatetime)
            day = result.group().split('일')[0]
            idatetime = now - datetime.timedelta(days=int(day))
            idatetime = idatetime.strftime('%Y.%m.%d.')

        title = response.meta['title']
        url = response.meta['url']
        press = response.meta['press']
        contents = response.text # 전체 기사 페이지 텍스트를 가지고 옴

        news_items['title'] = title
        news_items['url'] = url
        news_items['press'] = press
        news_items['contents'] = contents.strip()
        news_items['datetime'] = idatetime
        yield news_items

