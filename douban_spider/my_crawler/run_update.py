# -*- coding: utf-8 -*-
# @Time    : 2018/12/11 19:29
# @Author  : hujie
# @Info  : 文件说明
from scrapy.cmdline import execute

execute("scrapy crawl movie_update -s LOG_FILE=../logs/update_spider.log".split())
