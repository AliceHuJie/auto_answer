# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class MovieItem(Item):
    id = Field()
    title = Field()
    year = Field()
    region = Field()
    language = Field()
    director = Field()
    type = Field()
    actor = Field()
    date = Field()
    runtime = Field()
    rate = Field()
    rating_num = Field()


class PersonItem(Item):
    collection = 'person'
    id = Field()
    title = Field()
    year = Field()
    region = Field()
    language = Field()
    director = Field()
    type = Field()
    actor = Field()
    date = Field()
    runtime = Field()
    rate = Field()
    rating_num = Field()
