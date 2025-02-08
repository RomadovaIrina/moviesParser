# Парсер информации о фильмах https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту

1. Клонирование репозитория
```sh
git clone https://github.com/RomadovaIrina/moviesParser.git
cd movie_parser
```

2. Установка зависимостей
```sh
pip install -r requirements.txt
```

3. Запуск парсера
```sh
scrapy crawl movies_info -o <имя выходного файла>
```

4.а Для проверки получения рейтинга imdb без API не самым подходящим образом можно просто запустить код из ветки imdb_1

4.б Для проверки работы пполучения рейтинга imdb с помощью API (ветка imdb_2) нужно создать .env файл

Создать файл .env в корне проекта и добавить в него API-ключ OMDB:
```py
OMDB_API_KEY = <api_key>
```
Получить его можно по: https://www.omdbapi.com/apikey.aspx
К сожалению для бесплатной версии количество запросов в день ограничено, но все же лучше чем ничего.
