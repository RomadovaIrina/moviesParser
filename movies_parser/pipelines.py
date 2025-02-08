# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re


class MoviesParserPipeline:
    def process_item(self, item, spider):
        for field in ["genre", "director", "country", "year", "imdb_rating"]:
            if field in item:
                item[field] = re.sub(r"\s*\[[^\]]+\]", "", item[field]).strip()
        return item
