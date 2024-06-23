#!/usr/bin/python3 

# -*- coding:utf-8 -*-

import base64
import os
import json
import sys
import logging
import requests
from telebot import TeleBot


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stderr),],
    format="%(levelname)s:     %(message)s"
)

BOT_KEY = os.environ["BOT_KEY"]
URL = "http://nn:" + str(os.environ["PORT_NN_SERVICE"]) + "/predict"

bot = TeleBot(BOT_KEY)

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.send_message(
        message.from_user.id,
        f"<b>Привет, {message.from_user.first_name}!</b>\nЭтот бот умеет распознавать цифру на картирках.\nПросто отправь ему картинку ;)",
        parse_mode="HTML"
    )

@bot.message_handler(content_types=['photo'])
def get_users_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    logging.info(msg=f'User `{message.from_user.id}` upload image')
    data = base64.b64encode(downloaded_file).decode('utf-8')
    json_data = {"image": data}
    try:
        logging.info(msg='Start image recognition')
        response = requests.post(URL, json=json_data)
        res = json.loads(response.text)
        logging.info(msg=f'App answer: {res}')
        if res["status"] == "ok":
            bot.send_message(
                message.from_user.id,
                f'Отлично!\nТы отправил цифру: <b>{res["result"]}</b>',
                parse_mode="HTML"
            )
            return
        if res["status"] == "error":
            if res["result"] == "not digit":
                bot.send_message(
                    message.from_user.id,
                    "Уууупс, что-то пошло не так =(\nПохоже на твоей картинке нет цифры.\nПопробуюй еще разок.",
                    parse_mode="HTML"
                )
                return
            bot.send_message(
                message.from_user.id,
                f'Уууупс, что-то пошло не так =(\nОшибка: {res["result"]}',
                parse_mode="HTML"
            )
            return
    except Exception as ex:
        logging.error(msg=ex)
        bot.send_message(
            message.from_user.id,
            "Уууупс, что-то пошло не так =(\nОбратитесь к владельцу сервиса.",
            parse_mode="HTML"
        )
        raise

logging.info(msg='TG-bot starting')
bot.infinity_polling(none_stop=True, interval=0)
