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


TOKEN = "6958719692:AAGZ4bp_QrWl3axiWVYcaIzKYG_-_fKrMDQ"


embeddings =HuggingFaceEmbeddings(model_name='intfloat/e5-base')
#можно на гпу запускать
reader = easyocr.Reader(['ru'],gpu=False)

# Открываем файл и загружаем его содержимое как JSON
with open("цены.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Создаем список для хранения названий продуктов
product_names = []
products_and_prices ={}

# Проходим по каждой категории товаров
for category in data["Товар по категорям"]:
    # Проходим по каждому товару в категории
    for product_dict in category.values():
        # Проходим по каждому товару в словаре товаров
        for product_name in product_dict:
            # Добавляем название товара в список
            name=list(product_name.keys())[0]
            product_names.append(name)
            products_and_prices[name]=product_name.get(name)
            

store = FAISS.from_texts(product_names, embeddings)


            
print(product_names)

# Создание клавиатуры
def get_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "Отправить фото с ценой", callback_data="photo_with_price"
            )
        ],
        [
            InlineKeyboardButton(
                "Отправить фото с координатами", callback_data="photo_with_coords"
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
        await query.edit_message_text(text=f"Отправьте фото с ценой")
    if text == "photo_with_coords":
        await query.edit_message_text(text=f"Сначала отправьте фото")

def recognize_photo(file):
    results = reader.readtext(bytes(file))
    text = ' '.join([result[1] for result in results])
    print(text)
    questions_search_result=store.similarity_search_with_score(text,k=1)
    result=questions_search_result[0][0].page_content
    print(result)
    return result
            
            
            
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_option = context.user_data.get("selected_option", None)

    if selected_option == "photo_with_coords":
        photo_file = await update.message.photo[-1].get_file()
        file=await photo_file.download_as_bytearray()
        category=recognize_photo(file)
        del file
        
        await update.message.reply_text("Категория: "+category+'\nУстановленная цена: '+str(products_and_prices.get(category)[0])+' - '+str(products_and_prices.get(category)[1])+'\nТеперь пришлите геопозицию')
    elif selected_option == "photo_with_price":
        photo_file = await update.message.photo[-1].get_file()
        file=await photo_file.download_as_bytearray()
        category=recognize_photo(file)
        del file
        
        await update.message.reply_text("Категория: "+category+'\nУстановленная цена: '+str(products_and_prices.get(category)[0])+' - '+str(products_and_prices.get(category)[1])   )
        context.user_data["selected_option"] = None
        await update.message.reply_text(
            "Если хотите узнать что-то еще - выберите опцию",
            reply_markup=get_keyboard(),
        )
    else:
        await update.message.reply_text("Вы прислали фото не выбрав опцию", reply_markup=get_keyboard())


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_location = update.message.location
    selected_option = context.user_data.get("selected_option", None)
    if selected_option == "photo_with_coords":
        await update.message.reply_text(
            f"Вы прислали геопозицию вдобавок в фото. Ваше местоположение: {user_location.latitude}, {user_location.longitude}"
        )
        context.user_data["selected_option"] = None
        await update.message.reply_text(
            "Если хотите узнать что-то еще - выберите опцию",
            reply_markup=get_keyboard(),
        )
        
    else:
        await update.message.reply_text("Вы прислали геопозицию не выбрав опцию", reply_markup=get_keyboard())


def main():
    app = Application.builder().token(TOKEN).build()

    photo_handler = MessageHandler(filters.PHOTO, handle_photo)
    app.add_handler(photo_handler)
    location_handler = MessageHandler(filters.LOCATION, handle_location)
    app.add_handler(location_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()


if __name__ == "__main__":
    main()
