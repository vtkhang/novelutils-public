"""Define here the models for your scraped items

.. _See documentation in:
   https://docs.scrapy.org/en/latest/topics/items.html

"""

from scrapy import Field, Item


class NovelInfo(Item):
    """Store novel info."""
    title = Field()
    author = Field()
    url = Field()
    types = Field()
    foreword = Field()


class Chapter(Item):
    """Store novel chapters."""
    chapter_title = Field()
    chapter_content = Field()
