# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LazadaCrawlingItem(scrapy.Item):
    product_name = scrapy.Field
    product_price = scrapy.Field
    product_desc = scrapy.Field
    product_category = scrapy.Field
