# import scrapy
# from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
# import re
# from movies_parser.items import MoviesParserItem


# class MoviesInfoSpider(scrapy.Spider):
#     name = "movies_info"
#     allowed_domains = ["ru.wikipedia.org"]


#     custom_settings = {
#         'FEED_FORMAT': 'csv',
#         'FEED_URI': 'movies.csv',
#         'FEED_EXPORT_FIELDS': ['title', 'genre', 'director', 'country', 'year'],
#     }

#     def start_requests(self):
#         urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)

#     def parse(self, response):
#         current_page = response.meta.get('page', 1)
#         # #mw-pages > div.mw-content-ltr > div > div:nth-child(1) > ul > li > a
#         for element in response.css('#mw-pages div.mw-category-group ul li a'):
#             title = element.css('::text').get()
#             link = element.css('::attr(href)').get()
#             if title and link:
#                 yield scrapy.Request(
#                     url=response.urljoin(link),
#                     callback= self.parse_movie,
#                     meta={'title': title}
#                 )
                
#         next_page = response.css('a:contains("Следующая страница")::attr(href)').get()
#         if next_page:
#             next_page_url = response.urljoin(next_page)

#             parsed_url = urlparse(next_page_url)
#             query = parse_qs(parsed_url.query)
#             query['_'] = [str(current_page + 1)] 
            
#             unique_url = urlunparse(parsed_url._replace(
#                 query=urlencode(query, doseq=True)
#             ))
            
#             unique_url = unique_url.replace('w/index.php', 'wiki')

#             yield scrapy.Request(
#                 url=unique_url,
#                 callback=self.parse,
#                 meta={'page': current_page + 1}
#             )

  

#     def process_text(self, text_list):
#         if not text_list:
#             return "Не указано"
#         clean_items = []
#         for text in text_list:
#             text = text.strip()
#             # Пропускаем артефакты от парсинга (реально местами парсился css вместе с текстом в некоторых полях)
#             if not text or any(tag in text for tag in ['{', '}', 'mw-parser-output', 'color:']):
#                 continue
#             clean_items.append(text)
#         text = ' '.join(clean_items)
#         # Выкидываем скобки - примечания от википедии:  [1] [вд] [ ссылка ] и тп
#         text = re.sub(r'\s*\[[^\]]+\]', '', text)
#         # делаем красоту
#         text = text.replace(' ,', ',').replace(' .', '.').strip()

#         return text



#     def parse_movie(self, response):
#         title = response.meta['title']
#         item = MoviesParserItem()
#         # Я намучалась с селекторами, 
#         # у меня дикие проблемы с вытаскиванием жанров получались поэтому xpath
#         genre = self.process_text(response.xpath(
#             '//th[contains(., "Жанр")]/following-sibling::td//text()'
#         ).getall())

#         director = self.process_text(response.xpath(
#             '//th[contains(., "Режиссёр") or contains(., "Режиссёры")]/following-sibling::td//a/text() | '
#             '//th[contains(., "Режиссёр") or contains(., "Режиссёры")]/following-sibling::td//text()'
#         ).getall())

#         country = self.process_text(response.xpath(
#             '//th[contains(., "Страна") or contains(., "Страны")]/following-sibling::td//a/text() | '
#             '//th[contains(., "Страна") or contains(., "Страны")]/following-sibling::td//text()'
#         ).getall())

#         year = self.process_text(response.xpath(
#             '//th[contains(., "Год") or contains(., "Дата выхода")]/following-sibling::td//text()'
#         ).getall())

#         yield {
#             'title': title,
#             'genre': genre,
#             'director': director,
#             'country': country,
#             'year': year
#         }

import scrapy
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import re
from movies_parser.items import MoviesParserItem


class MoviesInfoSpider(scrapy.Spider):
    name = "movies_info"
    allowed_domains = ["ru.wikipedia.org"]


    def start_requests(self):
        urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        current_page = response.meta.get('page', 1)
        # #mw-pages > div.mw-content-ltr > div > div:nth-child(1) > ul > li > a
        for element in response.css('#mw-pages div.mw-category-group ul li a'):
            title = element.css('::text').get()
            link = element.css('::attr(href)').get()
            if title and link:
                yield scrapy.Request(
                    url=response.urljoin(link),
                    callback= self.parse_movie,
                    meta={'title': title}
                )
                
        next_page = response.css('a:contains("Следующая страница")::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)

            parsed_url = urlparse(next_page_url)
            query = parse_qs(parsed_url.query)
            query['_'] = [str(current_page + 1)] 
            
            unique_url = urlunparse(parsed_url._replace(
                query=urlencode(query, doseq=True)
            ))
            
            unique_url = unique_url.replace('w/index.php', 'wiki')

            yield scrapy.Request(
                url=unique_url,
                callback=self.parse,
                meta={'page': current_page + 1}
            )

  

    def process_text(self, text_list):
        if not text_list:
            return "Не указано"
        clean_items = []
        for text in text_list:
            text = text.strip()
            # Пропускаем артефакты от парсинга (реально местами парсился css вместе с текстом в некоторых полях)
            if not text or any(tag in text for tag in ['{', '}', 'mw-parser-output', 'color:']):
                continue
            clean_items.append(text)
        text = ' '.join(clean_items)
        # Выкидываем скобки - примечания от википедии:  [1] [вд] [ ссылка ] и тп
        text = re.sub(r'\s*\[[^\]]+\]', '', text)
        # делаем красоту
        text = text.replace(' ,', ',').replace(' .', '.').strip()

        return text



    def parse_movie(self, response):
        item = MoviesParserItem()
        item["title"] = response.meta['title']
        # Я намучалась с селекторами, 
        # у меня дикие проблемы с вытаскиванием жанров получались поэтому xpath
        item["genre"] = self.process_text(response.xpath(
            '//th[contains(., "Жанр")]/following-sibling::td//text()'
        ).getall())

        item["director"] = self.process_text(response.xpath(
            '//th[contains(., "Режиссёр") or contains(., "Режиссёры")]/following-sibling::td//a/text() | '
            '//th[contains(., "Режиссёр") or contains(., "Режиссёры")]/following-sibling::td//text()'
        ).getall())

        item["country"] = self.process_text(response.xpath(
            '//th[contains(., "Страна") or contains(., "Страны")]/following-sibling::td//a/text() | '
            '//th[contains(., "Страна") or contains(., "Страны")]/following-sibling::td//text()'
        ).getall())

        item["year"] = self.process_text(response.xpath(
            '//th[contains(., "Год") or contains(., "Дата выхода")]/following-sibling::td//text()'
        ).getall())

        yield item
