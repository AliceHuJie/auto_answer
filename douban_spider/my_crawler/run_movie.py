# -*- coding: utf-8 -*-
# @Time    : 2018/12/11 19:20
# @Author  : hujie
# @Info  : 文件说明
from datetime import datetime

from scrapy.cmdline import execute

time = datetime.now().strftime('%Y-%m-%d')
log_file = 'logs/movie_spider' + time + '.log'
execute(["scrapy", "crawl", "movie", "-s", "LOG_FILE=" + log_file])
