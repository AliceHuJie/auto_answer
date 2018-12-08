from scrapy.cmdline import execute

execute(["scrapy", "crawl", "movie", "-a", "deltafetch_reset=1"])
# 额外参数deltafetch_reset=1 是清空爬过的记录，使得数据可以重复爬取
