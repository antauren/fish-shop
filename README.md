## MVP Fish-shop bot

Проект магазина по продаже рыбы через Telegram

MVP версия проекта позволяет:
- Выбрать нужный товар в меню
- Добавлять товары в корзину
- Удалять товары из корзины
- Посмотреть корзину
- Оставить контакты покупателя для обратной связи

<img src="screenshots/fish-shop.gif"/>    

Пример работы бота: @antauren_fish_shop_bot

## Как установить

- Создайте магазин в [Elasticpath](https://www.elasticpath.com/)
- Создайте базу данных в [RedisLabs](https://redislabs.com/)
- Создайте бота [Telegram messenger](https://web.telegram.org/#/login)

- Установить [Python3](https://www.python.org/downloads/)
- Установите зависимости:
    ```
    pip install -r requirements.txt
    ```

Создать в корне проекта файл `.env` и прописать в нем переменные следующим образом:

```
ELASTICPATH_CLIENT_ID=3eSrFJPC50DAFuUhqf2qvLhGf3HwyFPvB3mB93LStv
ELASTICPATH_CLIENT_SECRET=ee1O0w5hDObQIZoa5ezpcC7pP2AWOb0yXTUamRLJ7V

TELEGRAM_TOKEN=5872136171:AAFPcxfBeh0ejlE3iTOfbqNv9DAkH_c4vGJ

DATABASE_PASSWORD=xSOWV51GKj1m52EytYNMRNHNIR6XAdvJ
DATABASE_HOST=redis-1324.c100.us-east-2-5.ec2.cloud.redislabs.com
DATABASE_PORT=16633
```



## Как запустить.
```
python3 bot.py
```




## Цель проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org/modules/chat-bots/lesson/fish-shop/).