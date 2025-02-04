import scrapy
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


class MoviesInfoSpider(scrapy.Spider):
    name = "movies_info"
    allowed_domains = ["ru.wikipedia.org"]
    # start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]


    def start_requests(self):
        urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        current_page = response.meta.get('page', 1)

        i=1 
# #mw-pages > div.mw-content-ltr > div > div:nth-child(1) > ul > li > a
        # for element in response.css('div.mw-category-group ul li a'):
        for element in response.css('#mw-pages div.mw-category-group ul li a'):
            title = element.css('::text').get()
            link = element.css('::attr(href)').get()
            if title:
                yield {
                    'title': title,
                    'link': response.urljoin(link)
                }
                
        next_page = response.css('a:contains("Следующая страница")::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)

            parsed_url = urlparse(next_page_url)
            query = parse_qs(parsed_url.query)
            query['_'] = [str(current_page + 1)] 
            
            unique_url = urlunparse(parsed_url._replace(
                query=urlencode(query, doseq=True)
            ))

            yield scrapy.Request(
                url=unique_url,
                callback=self.parse,
                meta={'page': current_page + 1}
            )

