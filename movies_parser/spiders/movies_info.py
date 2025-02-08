import os
import re
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

import requests
import scrapy
from dotenv import load_dotenv

from movies_parser.items import MoviesParserItem


class MoviesInfoSpider(scrapy.Spider):
    name = "movies_info"
    allowed_domains = ["ru.wikipedia.org", "www.imdb.com"]

    def start_requests(self):
        """Начальные ссылки для парсинга Википедии"""
        urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Парсинг текущей страницы фильмов и переход на следующие страницы"""
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
            next_page_url = self.make_next_url(response.urljoin(next_page), current_page)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={'page': current_page + 1}
            )
    
    def make_next_url(self, next_page_url: str, current_page: int) -> str:
        """Обработка параметров для получения ссылки на следующую страницу"""
        parsed_url = urlparse(next_page_url)
        query = parse_qs(parsed_url.query)
        query['_'] = [str(current_page + 1)] 
            
        unique_url = urlunparse(parsed_url._replace(
                query=urlencode(query, doseq=True)
        ))
        # По умолчанию url имеют вид https://ru.wikipedia.org/w/index.php?title
        # Такие url блокируются robots.txt, поэтому преобразуем  
        unique_url = unique_url.replace('w/index.php', 'wiki')
        return unique_url

  

    def process_text(self, text_list):
        """Приведение текста полученных данных к более понятному формату
            разбираемся с артефактами парсинга данных"""
        if not text_list:
            return None
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
        """Получение информации по фильму: режиссер, год/дата, жанр/жанры, страна/страны"""
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

        
        imdb_link = response.xpath('//th[contains(., "IMDb")]/following-sibling::td//a/@href').get()
    
        if imdb_link:
            yield scrapy.Request(
                url=response.urljoin(imdb_link),
                callback=self.parse_imdb,
                meta={"item": item}  # Передаем item через meta
        )
        else:
            item["imdb_rating"] = None
            yield item

    def parse_imdb(self, response):
        item = response.meta['item']
        rating = response.css('div[data-testid="hero-rating-bar__aggregate-rating__score"] span::text').get()
        try:
            item['imdb_rating'] = float(rating) if rating else None
        except ValueError:
            item['imdb_rating'] = None
        
        yield item
