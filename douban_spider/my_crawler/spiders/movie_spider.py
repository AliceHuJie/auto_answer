# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:44
# @Author  : hujie
# @Info  : 从movie_crawer

import json
import logging
import re
import traceback
from urllib import parse

from scrapy import Request, Selector, Spider

from douban_spider.my_crawler.items import *
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS

year_list = list(range(2018, 1990, -1))
country_list = [u'中国大陆', u'美国', u'香港', u'台湾', u'日本', u'韩国', u'英国', u'法国', u'德国', u'意大利', u'西班牙', u'印度', u'泰国', u'俄罗斯',
                u'伊朗', u'加拿大',
                u'澳大利亚', u'爱尔兰', u'瑞典', u'巴西', u'丹麦']


class MovieSpider(Spider):
    name = "movie"
    allowed_domains = ["movie.douban.com"]
    # sort = R 按上映时间逆序
    film_listurl = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags={tag}&start={page}&countries={country}&year_range={year},{year}'
    film_url = 'https://movie.douban.com/subject/{id}/'
    tag = parse.quote('电影')

    def start_requests(self):
        print('Movie Spider Start ...')
        logging.info('Movie Spider Start ...')
        for country in country_list[:1]:  # 国家在前，先爬完一个国家所有年份的电影
            c = parse.quote(country)
            for year in year_list[1:2]:  # len(year_list)
                for page in range(0, 100):
                    logging.warn('country:' + country + ' year:' + str(year) + ' page:' + str(page))
                    start = page * 20
                    yield Request(self.film_listurl.format(tag=self.tag, country=c, year=year, page=start),
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
            film_list = result.get('data')
            if film_list is not []:
                for film in film_list:
                    id = film.get('id')  # 获取电影id
                    title = film.get('title')
                    # logging.getLogger(__name__).info("已获取电影id：%s %s" % (title, id))
                    # print("已获取电影id：%s %s" % (title, id))
                    yield Request(self.film_url.format(id=id), callback=self.parse_film, meta={'id': id})
                    # id = 30214034
                    # yield Request(self.film_url.format(id=id), callback=self.parse_film, meta={'id': id})

    def parse_film(self, response):
        """
        解析单部电影详情信息
        :param response: Response对象
        :return:
        """
        film_info_item = MovieItem()
        id = response.meta.get('id')
        print("已爬取电影页面，id: %s" % id)
        try:
            selector = Selector(response=response)
            # 电影名字
            title = selector.xpath('//span[@property="v:itemreviewed"]/text()').extract()[0]
            # 年份
            try:
                year = selector.xpath('//*[@id="content"]/h1/span[2]/text()').extract()[0][1:5]
            except IndexError:
                year = ''

            # 导演
            director = selector.xpath('//*[@rel="v:directedBy"]/text()').extract()
            director_href = selector.xpath('//*[@rel="v:directedBy"]/@href').extract()
            director_ids = extract_ids_from_hrefs(director_href)
            # 编剧
            if selector.xpath('//*[@id="info"]/span[2]/span[1]/text()').extract_first() == '编剧':
                # 因为编剧这一项根据具体序号的span获取，因此先判断编剧项是否存在
                scenarist = selector.xpath('//*[@id="info"]/span[2]/span[2]/a/text()').extract()
                scenarist_href = selector.xpath('//*[@id="info"]/span[2]/span[2]/a/@href').extract()
                scenarist_ids = extract_ids_from_hrefs(scenarist_href)

            else:
                scenarist = []
                scenarist_ids = []
            # 演员
            actor = selector.xpath('//*[@rel="v:starring"]/text()').extract()
            # 演员ids
            actor_href = selector.xpath('//*[@rel="v:starring"]/@href').extract()
            actor_ids = extract_ids_from_hrefs(actor_href)
            # 类型
            genre = selector.xpath('//*[@property="v:genre"]/text()').extract()
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
            # 替换掉文本中的英文的单引号和双引号，防止插入语句有问题
            description = ''.join(description).strip().replace('\'', '“').replace('\"', '”')

            field_map = {
                'id': id,
                'title': title,
                'year': year,
                'region': ''.join(region).strip(),
                'language': ''.join(language).strip(),
                'director': '/'.join(director).strip(),
                'genre': '/'.join(genre).strip(),  # 要作为字段存的都转为str
                'actor': '/'.join(actor).strip(),
                'date': '/'.join(date).strip(),
                'runtime': ''.join(runtime).strip(),
                'rate': ''.join(rate),
                'rating_num': ''.join(rating_num),
                'director_ids': director_ids,  # list
                'actor_ids': actor_ids,  # list
                'description': description,
                'scenarist': '/'.join(scenarist),
                'scenarist_ids': scenarist_ids,  # list
                'alias': ''.join(alias).strip()
            }

            for field, attr in field_map.items():
                film_info_item[field] = attr
            yield film_info_item
        except Exception as e:
            logging.error('some error happened with movie : %s' % id)
            logging.error(traceback.print_exc(e))
            traceback.print_exc(e)


def extract_ids_from_hrefs(hrefs):
    """
    从href中得到人的id,/celebrity/2345  => 2345
    :param hrefs: 
    :return: ids
    """
    ids = []
    for href in hrefs:
        id_match = re.findall('/celebrity/(.*)/', href)
        if len(id_match) > 0:
            ids.append(id_match[0])
    return ids
