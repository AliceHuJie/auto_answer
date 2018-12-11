# -*- coding: utf-8 -*-
# @Time    : 2018/12/10 19:27
# @Author  : hujie
# @Info  : 文件说明
from scrapy.cmdline import execute

execute(["scrapy", "crawl", "movie_update", "-a", "deltafetch_reset=1"])
# 额外参数deltafetch_reset=1 是清空爬过的记录，使得数据可以重复爬取
