# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class MovieItem(Item):
    table = 'movie'
    id = Field()
    title = Field()
    year = Field()
    director = Field()
    director_ids = Field()
    scenarist = Field()
    actor = Field()
    actor_ids = Field()
    type = Field()
    region = Field()
    language = Field()
    date = Field()
    runtime = Field()
    alias = Field()
    rate = Field()
    rating_num = Field()
    description = Field()


class ActorItem(Item):
    table = 'actor'
    id = Field()
    title = Field()
    year = Field()
    director = Field()
    director_ids = Field()
    actor = Field()
    actor_ids = Field()
    type = Field()
    region = Field()
    language = Field()
    date = Field()
    runtime = Field()
    rate = Field()
    rating_num = Field()
    description = Field()
