# Парсер информации о фильмах https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту

1. Клонирование репозитория

git clone https://github.com/RomadovaIrina/moviesParser.git
cd movie_parser

2. Установка зависимостей

pip install -r requirements.txt

3. Для проверки работы пполучения рейтинга imdb нужно создать .env файл

Создать файл .env в корне проекта и добавить в него API-ключ OMDB:
OMDB_API_KEY = <api_key>

Получить его можно по: https://www.omdbapi.com/apikey.aspx
К сожалению для бесплатной версии количество запросов в день ограничено, но все же лучше чем ничего.
