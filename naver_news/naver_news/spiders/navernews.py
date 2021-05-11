import scrapy
from lxml import html
from naver_news.items import NaverNewsItem
import pandas as pd
df = pd.read_csv('../언론사_코드_매핑.csv') # 네이버 뉴스에서 제공하는 언론사별 코드번호 매핑 파일
class NavernewsSpider(scrapy.Spider):
    
    name = 'navernews'
    
    def start_requests(self):
        global df
        ## 코로나 + 백신 으로 검색, 최근 6개월간, 언론사별(언론사코드), start 1, 11 로 10개씩 페이지네이션
        ## url 구성 = query(검색키워드), startdate, enddate, sort=1(최신순) news_office_checked(언론사코드), start(pagination start id)
        root_url = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EC%BD%94%EB%A1%9C%EB%82%98%20%EB%B0%B1%EC%8B%A0&sort=1&photo=0&field=0&pd=6&ds=2020.11.12&de=2021.05.11&mynews=1&office_type=1&office_section_code=1&news_office_checked={press_code}&nso=so:dd,p:6m,a:all&start={offset}'
        start_urls = [root_url.format(press_code=i, offset=1) for i in df['코드']] # 시작 url 구축
        
        for iurl in start_urls:
            yield scrapy.Request(
                url=iurl, 
                callback=self.parse_url
            )
    def parse_url(self, response):
        tree = html.fromstring(response.text)

        items = list(zip(*[tree.xpath('//div[@class="news_area"]/a/@title'),tree.xpath('//div[@class="news_area"]/a/@href'),tree.xpath('//a[@class="info press"]/text()')]))
        next_page = tree.xpath('//div[@class="sc_page"]/a[@class="btn_next"]/@aria-disabled')[0] 
        next_page_url = tree.xpath('//div[@class="sc_page"]/a[@class="btn_next"]/@href')[0] # 다음 페이지가 없을 경우, length 에러가 뜨면서 넘어감
        
        for item in items:
            yield scrapy.Request(
                url=item[1],
                callback=self.parse,
                meta={'title':item[0],'url':item[1],'press':item[2]}
            )
        if next_page == 'false': # 다음 페이지가 있을 경우
            yield scrapy.Request(
                url='https://search.naver.com/search.naver'+next_page_url,
                callback=self.parse_url,
            )
    def parse(self, response):
        news_items = NaverNewsItem()
        title = response.meta['title']
        url = response.meta['url']
        press = response.meta['press']
        contents = response.text # 전체 기사 페이지 텍스트를 가지고 옴

        news_items['title'] = title
        news_items['url'] = url
        news_items['press'] = press
        news_items['contents'] = contents.strip()

        yield news_items

