import asyncio
import aiohttp
import emoji

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bs4 import BeautifulSoup

import keyboards as kb
from config import TOKEN, API_KEY


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users = []
include_adult = {}
show_more = {}
events = {}
langs = {}
poster_url = 'https://image.tmdb.org/t/p/w500'


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    '''
    Processes incoming /start command, asking for language and adult content settings
    '''
    user_id = message.from_user.id

    users.append(user_id)
    langs[user_id] = 'en'
    include_adult[user_id] = 'false'
    events[user_id] = asyncio.Event()

    await greetings_message(user_id)

    events[user_id].clear()
    await language_message(user_id)
    await events[user_id].wait()

    events[user_id].clear()
    await adult_message(user_id)
    await events[user_id].wait()

    if langs[user_id] == 'ru':
        text = (
            'Отлично, мы можем начинать!\n'
            'Для того, чтобы найти фильм или сериал, просто напиши мне его название.'
        )
    else:
        text = (
            'OK, let\'s get started!\n'
            'To start searching send me a movie title.'
        )
    await bot.send_message(user_id, text)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    '''
    Shows help message on /help command
    '''
    user_id = message.from_user.id
    if langs[user_id] == 'ru':
        help_message = (
            'Для начала работы нужно указать настройки: в первый раз -- с помощью команды `start`, '
            'затем, если нужно что-то изменить -- с помощью команды `/settings`. '
            'После установки настроек можно начать пользоваться ботом\n\n'
            'Чтобы сделать запрос, просто отправь название фильма или сериала\n'
            '**Примеры запросов:**\n'
            '- Avengers: Infinity war\n'
            '- Die hard\n'
            '- Веном\n'
            '- Брат 2\n'
            '- Game of Thrones\n\n'
            '**Команды:**:\n'
            '- `/start` --- Первичная настройка\n'
            '- `/help` --- Помощь\n'
            '- `/settings` --- Обновление настроек\n'
        )
    else:
        help_message = (
            'First, you need to specify language and your willingness to see adult content by '
            'ending `/start` command to the bot. You can change it later by sending `/settings` '
            'command. After that, you can start using the bot.\n\n'
            'To make a query simply send me the title of the movie or the TV show'
            '**Query examples:**\n'
            '- Avengers: Infinity war\n'
            '- Die hard\n'
            '- Веном\n'
            '- Брат 2\n'
            '- Game of Thrones\n\n'
            '**Commands:**\n'
            '- `/start` --- Start the bot and specify some settings\n'
            '- `/help` --- Show commands description\n'
            '- `/settings` --- Update settings\n'
        )
    await message.reply(help_message, parse_mode='markdown')


@dp.message_handler(commands=['settings'])
async def process_settings_command(msg: types.Message):
    '''
    Updates settings on the incoming /settings command
    '''
    user_id = msg.from_user.id
    if langs[user_id] == 'ru':
        text = 'Что вы хотите изменить?'
    else:
        text = 'What do you want to change?'
    await bot.send_message(msg.from_user.id, text, reply_markup=kb.inline_settings_kb)


@dp.message_handler()
async def send_movies(msg: types.Message):
    '''
    Main function for showing found movies with metadata
    '''
    user_id = msg.from_user.id
    if user_id not in users:
        text = 'I am not going to answer this until you ask me politely. Send me /start command'
        await bot.send_message(user_id, text)
    else:
        global show_more
        global events
        show_more[user_id] = True
        movie_title = msg.text
        events[user_id] = asyncio.Event()

        movies = await get_movies(movie_title, user_id)
        if langs[user_id] == 'ru':
            text = 'Я нашел ' + str(len(movies)) + ' фильмов по запросу ' + movie_title
        else:
            text = 'I\'ve found ' + str(len(movies)) + ' movies upon request ' + movie_title
        await bot.send_message(user_id, text)

        for i in range(len(movies)):
            if show_more[user_id]:
                if i % 3 == 2 and i != len(movies) - 1:
                    show_more[user_id] = False
                    events[user_id].clear()
                    await render_movie(movies[i], msg, callback_more=True)
                    await events[user_id].wait()
                else:
                    await render_movie(movies[i], msg, callback_more=False)


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback(callback_query: types.CallbackQuery):
    '''
    Processes all callbacks from inline keyboards
    '''
    data = callback_query.data.split('_')
    user_id = callback_query.from_user.id
    global include_adult
    global show_more
    global langs
    global events
    await bot.answer_callback_query(callback_query.id)

    if data[0] == 'adult':
        include_adult[user_id] = data[1]
    elif data[0] == 'lang':
        langs[user_id] = data[1]
    elif data[0] == 'show':
        show_more[user_id] = True
    elif data[0] == 'settings':
        if data[1] == 'lang':
            await language_message(user_id)
        elif data[1] == 'adult':
            await adult_message(user_id)

    events[user_id].set()


async def render_movie(movie: dict, msg: types.Message, callback_more: bool):
    '''
    Processes a movie obtained by get_movies function into a user-friendly format
    '''
    user_id = msg.from_user.id
    year = movie['release_date'][:4]
    title = movie['title'] + ' (' + year + ')\n\n'
    rating = str(movie['vote_average']) + '/10'
    date = '\n\nRelease date: ' + movie['release_date'] + '\n'

    urls = await find_movie(movie['title'], movie['original_title'], str(year), user_id)

    watch_text = '\n\nLinks:\n'
    for url in urls:
        watch_text += url + '\n'

    if movie['poster_path']:
        poster = poster_url + movie['poster_path']
        await bot.send_photo(user_id, poster, title)
    else:
        await bot.send_message(user_id, title)

    if callback_more:
        await bot.send_message(
            user_id,
            movie['overview'] + date + rating + watch_text,
            reply_markup=kb.inline_more_movies_kb
        )
    else:
        await bot.send_message(user_id, movie['overview'] + date + rating + watch_text)


async def get_movies(movie_name: str, user_id):
    '''
    Makes request to TMDb API and finds all metadata to relevant movies
    '''
    if user_id not in include_adult.keys():
        include_adult[user_id] = 'false'
    if user_id not in langs.keys():
        langs[user_id] = 'en'
    params = {
        'api_key': API_KEY,
        'query': movie_name,
        'include_adult': include_adult[user_id],
        'language': langs[user_id]
    }

    response = []

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.themoviedb.org/3/search/movie', params=params) as resp:
            movies = await resp.json()
        async with session.get('https://api.themoviedb.org/3/search/tv', params=params) as resp:
            tvs = await resp.json()

    for movie in movies['results']:
        item = {}
        item['title'] = movie['title']
        item['original_title'] = movie['original_title']
        item['overview'] = movie['overview']
        item['release_date'] = movie['release_date']
        item['vote_average'] = movie['vote_average']
        item['vote_count'] = movie['vote_count']
        item['poster_path'] = movie['poster_path']
        response.append(item)

    for tv in tvs['results']:
        item = {}
        item['title'] = tv['name']
        item['original_title'] = tv['original_name']
        item['overview'] = tv['overview']
        item['release_date'] = tv['first_air_date']
        item['vote_average'] = tv['vote_average']
        item['vote_count'] = tv['vote_count']
        item['poster_path'] = tv['poster_path']
        response.append(item)

    response.sort(key=lambda item: item['vote_count'], reverse=True)

    return response


async def find_movie(title: str, original_title: str, year: str, user_id: int):
    '''
    Searches for links to watch
    '''
    rus_urls = [
        'https://www.ivi.ru',
        'https://okko.tv',
        'https://www.tvzavr.ru',
    ]
    trunc_rus_urls = ['.'.join(url.split('.')[:-1]) for url in rus_urls]
    google = 'https://www.google.ru/search'
    header = {
        'user-agent': (
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
        )
    }
    movies_links = []
    async with aiohttp.ClientSession() as session:
        for url, trunc_url in zip(rus_urls, trunc_rus_urls):
            params = {
                'q': 'site:' + url + ' ' + title + ' ' + year + ' смотреть',
            }
            async with session.get(google, params=params, headers=header) as resp:
                search_rsp = await resp.text()
                soup = BeautifulSoup(search_rsp, 'lxml')
                # await bot.send_message(user_id, soup.prettify())
                for link in soup.find_all('a'):
                    if link.get('href') and link.get('href').startswith(trunc_url):
                        movies_links.append(link.get('href'))
                        break

    eng_urls = [
        'https://www.popcornflix.com',
        'https://putlocker.vip',
        'https://123movies.la',
    ]
    trunc_eng_urls = ['.'.join(url.split('.')[:-1]) for url in eng_urls]
    google = 'https://www.google.com/search'
    header = {
        'user-agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/69.0.3497.92 Safari/537.36'
        )
    }
    async with aiohttp.ClientSession() as session:
        for url, trunc_url in zip(eng_urls, trunc_eng_urls):
            params = {
                'q': 'site:' + url + ' ' + original_title + ' ' + year + ' watch',
            }
            async with session.get(google, params=params, headers=header) as resp:
                search_rsp = await resp.text()
                soup = BeautifulSoup(search_rsp, 'lxml')
                for link in soup.find_all('a'):
                    if link.get('href') and link.get('href').startswith(trunc_url):
                        movies_links.append(link.get('href'))
                        break
    return movies_links


async def greetings_message(user_id: int):
    if langs[user_id] == 'ru':
        greetings_text = (
            'Привет!\n'
            'Я могу быть твоим верным помощником в поиске кинчиков и сериальчиков на вечер!\n'
            'Разреши мне узнать о тебе пару деталей:'
        )
    else:
        greetings_text = (
            'Hi!\n'
            'I can help you to find something to watch in the evenings!\n'
            'Let me know some details about you:'
        )
    await bot.send_message(user_id, greetings_text)


async def language_message(user_id: int):
    if langs[user_id] == 'ru':
        await bot.send_message(user_id, 'Выберите язык', reply_markup=kb.inline_lang_kb)
    else:
        text = (
            'Select your language\n\n'
            '*Note: If you select any language other than Russian and English, I will continue'
            ' to speak English with you, but movies will be shown on the selected language*'
        )
        await bot.send_message(user_id, text, parse_mode='markdown', reply_markup=kb.inline_lang_kb)


async def adult_message(user_id: int):
    if langs[user_id] == 'ru':
        adult_text = 'Хочешь ли ты, чтобы тебе показывались фильмы для взрослых? :strawberry:'
    else:
        adult_text = 'Do you want to see adult content? :strawberry:'

    await bot.send_message(user_id, emoji.emojize(adult_text), reply_markup=kb.inline_adult_kb)


if __name__ == '__main__':
    executor.start_polling(dp)
