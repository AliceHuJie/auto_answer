# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:44
# @Author  : hujie
# @Info  : 电影爬虫
import json
import logging
import re
from urllib import parse

from scrapy import Request, Selector, Spider

from douban_spider.my_crawler.items import *
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS

year_list = list(range(2018, 1990, -1))
country_list = ['中国大陆', '美国', '香港', '台湾', '日本', '韩国', '英国', '法国', '德国', '意大利', '西班牙', '印度', '泰国', '俄罗斯', '伊朗', '加拿大',
                '澳大利亚', '爱尔兰', '瑞典', '巴西', '丹麦']


class MovieSpider(Spider):
    name = "movie"

    allowed_domains = ["movie.douban.com"]
    # sort = R 按上映时间逆序
    film_listurl = 'https://movie.douban.com/j/new_search_subjects?sort=R&range=0,10&tags={tag}&start={page}&countries={country}&year_range={year},{year}'
    film_url = 'https://movie.douban.com/subject/{id}/'
    tag = parse.quote('电影')

    def start_requests(self):
        for country in country_list[:1]:  # 国家在前，先爬完一个国家所有年份的电影
            country = parse.quote(country)
            for year in year_list[:1]:  # len(year_list)
                for page in range(0, 1):
                    start = page * 20
                    yield Request(self.film_listurl.format(tag=self.tag, country=country, year=year, page=start),
                                  headers=DEFAULT_REQUEST_HEADERS,
                                  callback=self.parse)

    def parse(self, response):
        """
        解析页面，获取电影id，构造电影链接
        :param response: Response对象
        :return:
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data'):
            filmlist = result.get('data')
            if filmlist != []:
                for film in filmlist:
                    id = film.get('id')  # 获取电影id
                    title = film.get('title')
                    logging.getLogger(__name__).debug("已获取电影id：%s %s" % (title, id))
                    yield Request(self.film_url.format(id=id), callback=self.parse_film, meta={'id': id})

    def parse_film(self, response):
        """
        解析单部电影详情信息
        :param response: Response对象
        :return:
        """
        selector = Selector(response=response)
        # id
        id = response.meta.get('id')
        # 电影名字
        title = selector.xpath('//span[@property="v:itemreviewed"]/text()').extract()[0]
        # 年份
        try:
            year = selector.xpath('//*[@id="content"]/h1/span[2]/text()').extract()[0][1:5]
        except IndexError:
            year = None

        # 导演
        director = selector.xpath('//*[@rel="v:directedBy"]/text()').extract()
        director_href = selector.xpath('//*[@rel="v:directedBy"]/@href').extract()
        director_ids = [re.findall('/celebrity/(.*)/', href)[0] for href in director_href]
        # 编剧
        scenarist = selector.xpath('//*[@id="info"]').re('编剧:</span>\s(.*)<br>')
        # 演员
        actor = selector.xpath('//*[@rel="v:starring"]/text()').extract()
        # 演员ids
        actor_href = selector.xpath('//*[@rel="v:starring"]/@href').extract()
        actor_ids = [re.findall('/celebrity/(.*)/', href)[0] for href in actor_href]
        # 类型
        type = selector.xpath('//*[@property="v:genre"]/text()').extract()
        # 制片国家
        region = selector.xpath('//*[@id="info"]').re('制片国家/地区:</span>\s(.*)<br>')
        # 语言
        language = selector.xpath('//*[@id="info"]').re('语言:</span>\s(.*)<br>')
        # 上映日期
        date = selector.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
        # 片长
        runtime = selector.xpath('//span[@property="v:runtime"]/text()').extract()
        # 又名
        alias = selector.xpath('//*[@id="info"]').re('又名:</span>\s(.*)<br>')
        # 评分
        rate = selector.xpath('//strong[@property="v:average"]/text()').extract()
        # 评价人数
        rating_num = selector.xpath('//span[@property="v:votes"]/text()').extract()
        # 剧情简介
        description = selector.xpath('//*[@id="link-report"]/span/text()').extract()

        film_info_item = MovieItem()

        field_map = {
            'id': id, 'title': title, 'year': year, 'region': ''.join(region), 'language': ''.join(language),
            'director': director, 'type': type, 'actor': actor, 'date': '/'.join(date),
            'runtime': ''.join(runtime), 'rate': ''.join(rate), 'rating_num': ''.join(rating_num),
            'director_ids': director_ids,
            'actor_ids': actor_ids, 'description': ''.join(description), 'scenarist': scenarist, 'alias': ''.join(alias)
        }

        for field, attr in field_map.items():
            film_info_item[field] = attr

        yield film_info_item
