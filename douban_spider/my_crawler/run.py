# -*- coding: utf-8 -*-
# @Time    : 2018/12/9 12:44
# @Author  : hujie
# @Info  : 运行爬虫，启动爬虫的入口
from scrapy.cmdline import execute

# execute(["scrapy", "crawl", "movie"])
# 增量爬取电影，爬过的不会继续爬

execute(["scrapy", "crawl", "person"])
# 增量爬取演员信息， 不涉及增量其实

# execute(["scrapy", "crawl", "movie", "-a", "deltafetch_reset=1"])
# 额外参数deltafetch_reset=1 是清空爬过的记录，使得数据可以重复爬取
# 这个和movie_update_spider的区别在于update spider更新的信息会更少，不会更新导演，演员，类型等信息
