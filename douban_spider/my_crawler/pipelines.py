import datetime
import json
import logging

import pymysql
from scrapy.exporters import JsonItemExporter, CsvItemExporter

from douban_spider.my_crawler import settings


class DoubanPipeline(object):
    def process_item(self, item, spider):
        print(item)
        return item


class JsonExporterPipeline(object):
    """
    调用 scrapy 提供的json export 导出json文件
    """

    def __init__(self):
        self.file = open('douban_movie.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"  # 确保中文显示正常
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()


class EnrolldataPipeline(object):
    def open_spider(self, spider):
        self.file = open("movie.csv", "ab+")
        self.exporter = CsvItemExporter(self.file, include_headers_line=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        print(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.PORT,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        try:
            self.cursor.execute(
                "insert into article (body, author, createDate) value(%s, %s, %s) on duplicate key update author=(author)",
                (item['body'],
                 item['author'],
                 datetime.datetime.now()
                 ))
            self.connect.commit()
        except Exception as error:
            logging.log(error)
        return item

    def close_spider(self, spider):
        self.connect.close()
