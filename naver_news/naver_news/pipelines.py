# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter
from pymongo import MongoClient

class NaverNewsCrawlerPipeline:
    def __init__(self, mongo_db, mongo_client, mongo_collection):
        self.mongo_db = mongo_db
        self.mongo_client = mongo_client
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):  #settings.py 에서 MongoDB 정보 받아옴
        return cls(
            mongo_db =  crawler.settings.get('MONGO_DB'),
            mongo_client = crawler.settings.get('MONGO_CLIENT'),
            mongo_collection = crawler.settings.get('MONGO_COLLECTION')
        )
    
    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_db, 27017)  #받아온 MongoDB 정보에 연결
        self.collection = self.client[self.mongo_client][self.mongo_collection]

    
    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        compare = self.collection.find_one({'url':item['url']})

        if not compare:
            self.collection.insert_one(dict(item))  #중복되지 않는다면 추가
        # else:
        #     spider.close_down = True #중복되는 게 발견하면 크롤링을 중지

        return item['datetime']
        pass
