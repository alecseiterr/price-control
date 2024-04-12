from aiogram import Bot, Dispatcher, executor, types
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import asyncio

API_TOKEN = '7065235398:AAEcHg46fpq22s9ml4bcKgFCP-rNGzyZCH8'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Список наименований продуктов
product_names = [
    "Хлеб ржаной",
    "Хлеб пшеничный",
    "Молоко",
    "Кефир",
    "Сметана",
    "Творог",
    "Говядина",
    "Свинина",
    "Курица",
    "Колбасные изделия"
]

# Создаем TF-IDF векторы для наименований продуктов
vectorizer = TfidfVectorizer(min_df=1, analyzer='word', stop_words=None)
tfidf = vectorizer.fit_transform(product_names)
tfidf_np = tfidf.toarray().astype('float32')

# Создаем индекс Faiss
index = faiss.IndexFlatL2(tfidf_np.shape[1])  # Используем L2 расстояние
index.add(tfidf_np)  # Добавляем данные

async def search_product(query):
    query_vec = vectorizer.transform([query]).toarray().astype('float32')
    k = 3  # Найдем топ-3 ближайших продукта
    D, I = index.search(query_vec, k)
    results = []
    for i in range(k):
        results.append(f"{product_names[I[0][i]]}, Расстояние: {D[0][i]:.2f}")
    return "\n".join(results)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Это бот для контроля социальных цен. Отправьте мне название продукта, и я найду похожие товары.")

@dp.message_handler()
async def echo(message: types.Message):
    response = await search_product(message.text)
    await message.reply(f"Ближайшие продукты:\n{response}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)





