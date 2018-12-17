# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:45
# @Author  : hujie
# @Info  : 人的信息获取
import logging
import re
import traceback

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
    cursor = connect.cursor()

    def start_requests(self):
        print('Person Spider Start ...')
        logging.info('Person Spider Start ...')
        person_ids_query = 'SELECT person_id FROM person_crawer_manager where is_crawed = 0'
        count = self.cursor.execute(person_ids_query)
        if count == 0:
            print('No Person to Crawl, Person Spider Stop ...')
            logging.info('No Person to Crawl, Person Spider Stop ...')
            return
        for i in range(count):
            person_id = self.cursor.fetchone()[0]  # fetchone 得到的是一个一个元素的tuple
            # person_id = 1054531  # 用于debug
            yield Request(self.person_url.format(id=person_id), headers=DEFAULT_REQUEST_HEADERS, callback=self.parse)

    def parse(self, response):
        """
        解析演员信息页面，yield 演员item
        :param response: Response对象
        :return:
        """
        url = response.url
        id = re.findall("\d+", url)[0]
        print("已爬取演员信息页面，person_id: %s" % id)
        try:
            selector = Selector(response=response)
            # 名字
            name = selector.xpath('//*[@id="content"]/h1/text()').extract_first()
            basic_info = selector.xpath('//*[@id="headline"]/div[2]/ul').extract_first()
            basic_info = basic_info.replace('\n', '')
            image = selector.xpath('//*[@id="headline"]/div[1]/a/@href').extract_first()
            gender = re.findall('性别</span>:(.*?)</li>', basic_info)  # [男]
            biography = re.findall('星座</span>:(.*?)</li>', basic_info)  # [水瓶座]
            birthday = re.findall('出生日期</span>:(.*?)</li>', basic_info)  # [1978-02-17]
            birthplace = re.findall('出生地</span>:(.*?)</li>', basic_info)  # [中国,黑龙江,哈尔滨]
            occupation = re.findall('职业</span>:(.*?)</li>', basic_info)  # [演员/配音/编剧]
            more_cn = re.findall('更多中文名</span>:(.*?)</li>', basic_info)  # [张毅(原名)/小太爷(昵称)]
            more_cn = ''.join(more_cn)
            if more_cn is not '':
                more_cn = re.sub(u'\\(.*?\\)', '', more_cn)  # 去掉括号及中间内容
            more_fn = re.findall('更多外文名</span>:(.*?)</li>', basic_info)  # [Kong-sang Chan (本名) / Pao Pao (昵称)]
            more_fn = ''.join(more_fn).replace('\'', '')
            if more_fn is not '':
                more_fn = re.sub(u'\\(.*?\\)', '', more_fn)
                more_fn = more_fn.replace('"', '').replace('\'', '')  # 去掉特殊字符，避免导致插入语句错误
            introduction = selector.xpath('//*[@id="intro"]/div[2]/span[last()]/text()').extract_first()  # 从span标签提取
            if introduction is None:
                introduction = selector.xpath('//*[@id="intro"]/div[2]/text()').extract_first()  # 简介信息很短的直接在div中
            introduction = introduction.strip().replace('\'', '“').replace('\"', '”')

            person_item = PersonItem()
            field_map = {
                'id': id,
                'image': image,
                'cn_name': name.split(' ')[0],
                'fn_name': ''.join(name.split(' ')[1:]),
                'gender': ''.join(gender),  # 使用join而不是直接取list[0] : list为空时0会IndexError
                'birthday': ''.join(birthday),
                'birthplace': ''.join(birthplace),
                'biography': ''.join(biography),
                'introduction': introduction,
                'occupation': ''.join(occupation),
                'more_cn_name': more_cn,
                'more_fn_name': more_fn,
            }
            for field, attr in field_map.items():
                person_item[field] = attr.strip()
            yield person_item
        except Exception as e:
            logging.error('some error happened with crawl person : %s' % id)
            logging.error(traceback.print_exc(e))
            traceback.print_exc(e)
