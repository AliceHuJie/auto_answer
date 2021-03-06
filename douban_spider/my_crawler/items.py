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
    scenarist_ids = Field()
    actor = Field()
    actor_ids = Field()
    genre = Field()
    region = Field()
    language = Field()
    date = Field()
    runtime = Field()
    alias = Field()
    rate = Field()
    rating_num = Field()
    description = Field()


class PersonItem(Item):
    table = 'person'
    id = Field()
    image = Field()
    cn_name = Field()
    fn_name = Field()
    gender = Field()
    birthday = Field()
    birthplace = Field()
    biography = Field()
    introduction = Field()
    occupation = Field()
    more_cn_name = Field()
    more_fn_name = Field()


class TextItem(Item):
    id = Field()
    key = Field()
    description = Field()


class MvItem(Item):
    id = Field()
    title = Field()
    year = Field()
    country = Field()
