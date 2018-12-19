# -*- coding: utf-8 -*-
# @Time    : 2018/12/11 19:13
# @Author  : hujie
# @Info  : 文件说明
from datetime import datetime

from scrapy.cmdline import execute

time = datetime.now().strftime('%Y-%m-%d')
log_file = 'logs/person_spider' + time + '.log'
execute(["scrapy", "crawl", "person", "-a", "deltafetch_reset=1", "-s", "LOG_FILE=" + log_file])
