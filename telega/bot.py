# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import easyocr
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import re
from datetime import datetime
from PIL import Image
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd


TOKEN = "6958719692:AAGZ4bp_QrWl3axiWVYcaIzKYG_-_fKrMDQ"


# Настройка логирования с сохранением в файл
log_file = 'bot_activity.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создание FileHandler для записи логов в файл
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=5)  # 5 MB на файл, 5 ротаций
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавление FileHandler к логгеру
logger.addHandler(file_handler)

# Загрузка данных из CSV адреса и коорды
data_adress_distance = pd.read_csv('coordinats.csv')

def haversine_distance(lat1, lon1, lat2, lon2):
    # Радиус Земли в километрах
    R = 6371.0
    
    # Преобразование координат в радианы
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Разница координат
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Формула гаверсинуса
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    
    return distance

def find_nearest_address(user_lat, user_lon):

    
    # Предполагаем, что координаты хранятся в строковом формате, нужно их преобразовать
    data_adress_distance['Lat'] = data_adress_distance['Coordinates'].apply(lambda x: float(x.split(',')[0].strip('()')))
    data_adress_distance['Lon'] = data_adress_distance['Coordinates'].apply(lambda x: float(x.split(',')[1].strip('()')))
    
    # Вычисляем расстояние до каждой точки
    data_adress_distance['Distance'] = data_adress_distance.apply(lambda row: haversine_distance(user_lat, user_lon, row['Lat'], row['Lon']), axis=1)
    
    # Находим адрес с минимальным расстоянием
    nearest_location = data_adress_distance.loc[data_adress_distance['Distance'].idxmin()]
    
    return nearest_location['Address'], nearest_location['Distance']

#embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-base")
# можно на гпу запускать
reader = easyocr.Reader(["ru"], gpu=False)

# Открываем файл и загружаем его содержимое как JSON
with open("цены.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Создаем список для хранения названий продуктов
product_names = []
products_and_prices = {}
products_and_keywords={}
# Проходим по каждой категории товаров
for category in data["Товар по категорям"]:
    # Проходим по каждому товару в категории
    for product_dict in category.values():
        # Проходим по каждому товару в словаре товаров
        for product_name in product_dict:
            # Добавляем название товара в список
            name = list(product_name.keys())[0]
            product_names.append(name)
            products_and_prices[name] = product_name.get(name)
            products_and_keywords[name]=list(product_name.values())[0][2]

#store = FAISS.from_texts(product_names, embeddings)
print(products_and_keywords)


# Функция для поиска совпадений
def find_matches(text, keywords):
    matches = []
    for keyword in keywords:
        if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
            matches.append(keyword)
    return matches



print(product_names)


# Создание клавиатуры
def get_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "Узнать цену по фото", callback_data="photo_with_price"
            )
        ],
        [
            InlineKeyboardButton(
                "Узнать цену по фото и ближайший магазин", callback_data="photo_with_coords"
            )
        ],
        [
            InlineKeyboardButton(
                "Узнать ближайший магазин", callback_data="nearest_shop"
            )
        ],
        [
            InlineKeyboardButton(
                "Цена по названию товара", callback_data="get_price"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# функция-обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    await update.message.reply_text(
        f"{user.first_name}, приветствую! Я бот для социальных цен. Выберите нужную вам опцию",
        reply_markup=get_keyboard(),
    )


# Обработка кнопок клавиатуры
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    text = query.data
    context.user_data["selected_option"] = text
    if text == "photo_with_price":
        await query.edit_message_text(text=f"Отправьте фото с ценником")
    if text == "photo_with_coords":
        await query.edit_message_text(text=f"Сначала отправьте фото")
    if text == "nearest_shop":
        await query.edit_message_text(text=f"Отправьте вашу геопозицию")
    if text == "get_price":
        await query.edit_message_text(text=f"Напишите название товара")
def clean_string(text):
    # Паттерн для удаления всех символов кроме запятой, точки, дефиса, русских букв и буквенно-цифровых символов
    pattern = r'[^a-zA-Zа-яА-Я0-9,%.\-\s]'
    cleaned_text = re.sub(pattern, '', text)
    cleaned_text=cleaned_text.lower()
    return cleaned_text


def find_matched_categories(text):
    # Поиск совпадений
    matches = []
    for category, keywords in products_and_keywords.items():
        category_matches = find_matches(text, keywords)
        if category_matches:
            matches.append((category, category_matches))

    # Вывод результатов
    if matches != []:
        matched_categories=[]
        for category, matched_keywords in matches:
            matched_categories.append(category)
            return matched_categories
    else:
        return []
    
    
def recognize_photo(file):
    results = reader.readtext(bytes(file))
    text = " ".join([result[1] for result in results])
    text=clean_string(text)
    print(text)
    matched_categories=find_matched_categories(text)
    if matched_categories != []:
        return matched_categories
    else:
        return None





async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_option = context.user_data.get("selected_option", None)
    user_id=update.message.chat_id
    if selected_option == "photo_with_coords":
        photo_file = await update.message.photo[-1].get_file()
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")
        photo_path=f'./photos/photo_{str(user_id)}_{str(formatted_date)}.jpg'
        await photo_file.download_to_drive(photo_path)
        with open(photo_path, "rb") as file:
            image_bytes = file.read()
        categories = recognize_photo(image_bytes)
        
        del file
        
        if categories is not None:
            message=''
            for category in categories:
                message+="\n\nКатегория: "\
                + str(category)\
                + "\nУстановленная цена: "\
                + str(products_and_prices.get(category)[0])\
                + " - "\
                + str(products_and_prices.get(category)[1])+'\n'
            message+="\nТеперь пришлите геопозицию"
            await update.message.reply_text(
                'Обнаруженные товары:\n'+message
                
            )
            logger.info(f"user:({update.message.chat_id}). Отправил фото:({photo_path}). Найдены следущие категории ({categories})")
        else: 
            context.user_data["selected_option"] = None
            await update.message.reply_text(
                'Категории не найдены',
                reply_markup=get_keyboard(),
                
            )
            logger.info(f"user:({update.message.chat_id}). Отправил фото:({photo_path}). Категорий не найдено")
    elif selected_option == "photo_with_price":
        photo_file = await update.message.photo[-1].get_file()
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")
        photo_path=f'./photos/photo_{str(user_id)}_{str(formatted_date)}.jpg'
        await photo_file.download_to_drive(photo_path)
        with open(photo_path, "rb") as file:
            image_bytes = file.read()
        categories = recognize_photo(image_bytes)
        del file

        if categories is not None:
            message=''
            for category in categories:
                message+="\n\nКатегория: "\
                + str(category)\
                + "\nУстановленная цена: "\
                + str(products_and_prices.get(category)[0])\
                + " - "\
                + str(products_and_prices.get(category)[1])+'\n'
            
            await update.message.reply_text(
                'Обнаруженные товары:'+message
                
            )
            await update.message.reply_text(
            "Если хотите узнать что-то еще - выберите опцию",
            reply_markup=get_keyboard(),
            )
            logger.info(f"user:({update.message.chat_id}). Отправил фото:({photo_path}). Найдены следущие категории ({categories})")
        else: 
            await update.message.reply_text(
                'Категории не найдены',
                reply_markup=get_keyboard(),
                
            )
            logger.info(f"user:({update.message.chat_id}). Отправил фото:({photo_path}). Категорий не найдено")
        context.user_data["selected_option"] = None

    else:
        await update.message.reply_text(
            "Вы прислали фото не выбрав опцию", reply_markup=get_keyboard()
        )
        logger.info(f"user:({update.message.chat_id}). Отправил фото. Не выбрал кнопки на клавиатуре")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    selected_option = context.user_data.get("selected_option", None)
    if selected_option == "photo_with_coords": 
        # Координаты пользователя, полученные из Telegram
        user_coordinates = (user_location.latitude,user_location.longitude)
        # Нахождение ближайшего адреса
        nearest_address, distance = find_nearest_address(*user_coordinates)

        await update.message.reply_text(
            f"Ближайший адрес: {nearest_address}, Расстояние: {distance:.2f} км"
        )
        context.user_data["selected_option"] = None
        await update.message.reply_text(
            "Если хотите узнать что-то еще - выберите опцию",
            reply_markup=get_keyboard(),
        )
        logger.info(f"user:({update.message.chat_id}). Отправил координаты:({user_location}). Ближайший адрес: {nearest_address}, Расстояние: {distance:.2f} км")
        
    elif selected_option == "nearest_shop": 
        # Координаты пользователя, полученные из Telegram
        user_coordinates = (user_location.latitude,user_location.longitude)
        # Нахождение ближайшего адреса
        nearest_address, distance = find_nearest_address(*user_coordinates)

        await update.message.reply_text(
            f"Ближайший адрес: {nearest_address}, Расстояние: {distance:.2f} км"
        )
        context.user_data["selected_option"] = None
        await update.message.reply_text(
            "Если хотите узнать что-то еще - выберите опцию",
            reply_markup=get_keyboard(),)
        logger.info(f"user:({update.message.chat_id}). Отправил координаты:({user_location}). Ближайший адрес: {nearest_address}, Расстояние: {distance:.2f} км")
    else:
        await update.message.reply_text(
            "Вы прислали геопозицию не выбрав опцию", reply_markup=get_keyboard()
        )
        logger.info(f"user:({update.message.chat_id}). Отправил координаты:({user_location}). И не выбрал опцию")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_option = context.user_data.get("selected_option", None)
    if selected_option == "get_price":
        message=update.message.text 
        categories=find_matched_categories(message)
        if categories != []:
            message=''
            for category in categories:
                message+="\n\nКатегория: "\
                + str(category)\
                + "\nУстановленная цена: "\
                + str(products_and_prices.get(category)[0])\
                + " - "\
                + str(products_and_prices.get(category)[1])+'\n'
            
            await update.message.reply_text(
                'Обнаруженные товары:'+message
                
            )
            await update.message.reply_text(
                'Если хотите узнать что-то еще - выберите опцию',
                reply_markup=get_keyboard(),
                
            )
            logger.info(f"user:({update.message.chat_id}). Написал название товара:({update.message.text }). Найдены следущие категории ({categories})")
        else: 
            await update.message.reply_text(
                'Категории не найдены',
                reply_markup=get_keyboard(),
                
            )
            logger.info(f"user:({update.message.chat_id}). Написал название товара:({message}). Товаров не найдено")
        
        
    else:
        await update.message.reply_text(
            "Вы прислали текст выбрав неправильную опцию на клавиатуре", reply_markup=get_keyboard()
        )
        logger.info(f"user:({update.message.chat_id}). Написал текст:({update.message.text }). Не выбрав опцию на клавиатуре")
    context.user_data["selected_option"] = None
    
def main():
    app = Application.builder().token(TOKEN).build()

    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    app.add_handler(photo_handler)
    location_handler = MessageHandler(filters.LOCATION, handle_location)
    app.add_handler(location_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    text_handler = MessageHandler(filters.TEXT, handle_text)
    app.add_handler(text_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
