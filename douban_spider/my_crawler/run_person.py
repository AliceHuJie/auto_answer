# -*- coding: utf-8 -*-
# @Time    : 2018/12/11 19:13
# @Author  : hujie
# @Info  : 文件说明
from scrapy.cmdline import execute

execute("scrapy crawl person -s LOG_FILE=logs/person_spider.log".split())
