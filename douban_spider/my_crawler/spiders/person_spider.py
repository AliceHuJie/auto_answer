# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:45
# @Author  : hujie
# @Info  : 人的信息获取

import pymysql
from scrapy import Request, Selector, Spider

from douban_spider.my_crawler import settings
from douban_spider.my_crawler.items import *
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS


class PersonSpider(Spider):
    name = "person"

    allowed_domains = ["movie.douban.com"]
    person_url = 'https://movie.douban.com/celebrity/{id}/'
    connect = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.PORT,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        charset='utf8',
    )
    print(connect)
    cursor = connect.cursor()

    def start_requests(self):
        print('enter')
        person_ids_query = 'SELECT person_id FROM person_crawer_manager where is_crawed = 0'
        count = self.cursor.execute(person_ids_query)
        for i in range(20):
            person_id = self.cursor.fetchone()[0]  # fetchone 得到的是一个一个元素的tuple
            yield Request(self.person_url.format(id=person_id), headers=DEFAULT_REQUEST_HEADERS, callback=self.parse)

    def parse(self, response):
        """
        解析演员信息页面，yield 演员item
        :param response: Response对象
        :return:
        """
        person_info_item = PersonItem()
        print(response)
        url = response.url
        print(url)  # url中提取id
        print("已爬取演员信息页面，id: %s" % id)
        try:
            selector = Selector(response=response)
            # 名字
            name = selector.xpath('//*[@id="content"]/h1/text()').extract_first()
            person_info_item["name"] = name.split(" ")[0]
            person_info_item["more_name"] = " ".join(name.split(" ")[1:])

            gender = selector.xpath('//*[@id="info"]').re('性别:</span>\s(.*)<br>')
            biography = selector.xpath('//*[@id="info"]').re('星座:</span>\s(.*)<br>')
            birthday = selector.xpath('//*[@id="info"]').re('出生日期:</span>\s(.*)<br>')
            birthplace = selector.xpath('//*[@id="info"]').re('出生地:</span>\s(.*)<br>')
            occupation = selector.xpath('//*[@id="info"]').re('职业:</span>\s(.*)<br>')
            more_cn = selector.xpath('//*[@id="info"]').re('更多中文名:</span>\s(.*)<br>')
            more_fn = selector.xpath('//*[@id="info"]').re('更多外文名:</span>\s(.*)<br>')
            family = selector.xpath('//*[@id="info"]').re('家庭成员:</span>\s(.*)<br>')

        except:
            pass
