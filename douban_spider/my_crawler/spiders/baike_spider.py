# -*- coding: utf-8 -*-
# @Time    : 2018/12/22 14:46
# @Author  : hujie
# @Info  : 文件说明

import re
from urllib import parse

from scrapy import Request, Selector, Spider

from douban_spider.my_crawler.items import TextItem
from douban_spider.my_crawler.settings import BAIKE_REQUEST_HEADERS


class BaikeSpider(Spider):
    name = 'baike'
    allowed_domains = ["baike.baidu.com"]
    start_url = 'https://baike.baidu.com/item/{key}/{id}'
    start_key = '成龙'
    start_id = 71648

    def start_requests(self):
        key = parse.quote(self.start_key)
        yield Request(self.start_url.format(key=key, id=self.start_id),
                      headers=BAIKE_REQUEST_HEADERS,
                      callback=self.parse,
                      meta={'key': key, 'id': self.start_id})

    def parse(self, response):
        selector = Selector(response)

        # 提取文档中的其他链接，生成请求
        hrefs = selector.xpath('//a/@href ').extract()
        hrefs = set(hrefs)  # 去除一个页面中的相同链接
        for h in hrefs:
            match_result = re.match('^/item/(.*?)/(\d+).*', h)
            if match_result:
                url = 'https://baike.baidu.com' + h
                key = match_result.group(1)
                id = match_result.group(2)
                yield Request(self.start_url.format(key=key, id=id),
                              headers=BAIKE_REQUEST_HEADERS,
                              callback=self.parse,
                              meta={'key': key, 'id': id})

        # 解析当前页面，提取信息
        para_list = selector.xpath("//div[@class='para']").xpath('string(.)').extract()
        text = ''.join(para_list).replace('\n', '')
        patten = re.compile('\[\d+-?\d*\]')  # 去掉文本中的上下标文本 [1], [9-10] 之类的 *:0-多次 +：至少一次 ？ 0或一次
        text = re.sub(patten, '', text)
        text = text.replace('\'', '').replace('\"', '')  # 去掉特殊字符，以免导致sql错误
        item = TextItem()
        item['id'] = response.meta.get('id')
        item['key'] = parse.unquote(response.meta.get('key'), encoding='utf-8')
        item['description'] = text
        print('已获取词条: %s' % item['key'])
        yield item
