# Cinema Bot

A Telegram bot **[@vip_pro_best_cinema_bot](https://t.me/vip_pro_best_cinema_bot)** written on `aiogram` for finding movies by their titles.

## What can it do?

You simply send a movie or TV show title and get its poster, brief overview, release date and links to sites, where you can watch it (or buy it).
The bot supports 6 languages:
- Russian, English (fully supported)
- French, German, Spanish, Chinese (only queries and responses)

## How does it work?

It uses the open API of *The Movie Database (TMDb)* to find all metadata about relevant movies and TV shows sorted by their popularity. To find links to watch, it googles each movie on each site from the predefined set of online cinemas.

## How to use it?

First, you need to specify language and your willingness to see adult content by sending `/start` command to the bot. You can change it later by sending `/settings` command. After that, you can start using the bot.

## Commands

- `/start` --- Start the bot and specify some settings
- `/help` --- Show commands description
- `/settings` --- Update settings

## Query examples

- Avengers: Infinity war
- Die hard
- Веном
- Брат 2
- Игра престолов
