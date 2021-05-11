# naver news crawler

네이버 뉴스에서
코로나 + 백신 키워드로
현재기준 최근 6개월 뉴스기사를 수집하는 수집기 입니다.

수집된 기사들은 로컬 monogodb 에 저장됩니다.

- scrapy
- pandas
- lxml
- pymongo


#### mongodb 정보
- database : naver
- collection : news

```
title : 뉴스기사 타이틀
contents : 뉴스기사 본문 html
url : 뉴스기사 url
press : 언론사
datetime : 뉴스기사 작성시간
```
#### 데이터베이스 실행
```
docker-compose up -d
```

#### 수집기 실행
```
scrapy crawl navernews
```


#### 수집 실행 디버깅
![screensh](./scrapy_debug.jpg)