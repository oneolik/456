import csv
import time
import telebot
from telebot import types
import random
from collections import Counter

TOKEN = "8030905867:AAGvwEQEF1SaoIEEqmB-uWWFSje_9zcTgWg"
bot = telebot.TeleBot(TOKEN)

CSV_FILE = "stats.csv"

def save_stats(user_id, username, first_name, event_type, text, correct_answer=""):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow([
            user_id,
            username or "",
            first_name or "",
            event_type,
            text,
            correct_answer,
            time.strftime("%Y-%m-%d %H:%M:%S")
        ])

def print_analytics():
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as csvfile:
            rows = list(csv.reader(csvfile, delimiter=";"))

        if not rows:
            print("Аналитики пока нет")
            return

        users = set()
        events = Counter()
        correct = 0
        total = 0

        for row in rows:
            user_id, _, _, event, text, answer, _ = row
            users.add(user_id)
            events[event] += 1
            if event == "riddle_answer":
                total += 1
                if text.lower() == answer.lower():
                    correct += 1

        print("Пользователи:", len(users))
        print("События:", len(rows))
        print("Факты:", events["fact"])
        print("Цитаты:", events["quote"])
        print("Загадки:", events["riddle_sent"])
        print("Ответы:", total)
        print("Верные:", correct)

    except FileNotFoundError:
        print("Файл stats.csv ещё не создан")

facts = [
    "Меркурий — самая маленькая планета Солнечной системы.",
    "Венера вращается в противоположную сторону от большинства планет.",
    "Марс называют Красной планетой из-за оксида железа.",
    "На Марсе находится самая высокая гора в Солнечной системе — Олимп.",
    "Юпитер — крупнейшая планета, его масса больше всех остальных вместе взятых.",
    "День на Венере длиннее года.",
    "Сатурн мог бы плавать в воде, если бы нашёлся подходящий океан.",
    "На Луне есть следы людей, которым миллионы лет не грозит исчезновение."
]

quotes = [
    "В космосе нет границ, есть только возможности.",
    "Смотри на Землю — и понимай, как мы малы.",
    "Каждый день космонавта — шаг к новым открытиям.",
    "Оказавшись в космосе, ты понимаешь, насколько уязвима Земля.",
    "Планета — колыбель разума, но нельзя вечно жить в колыбели.",
    "Человек — это солнце, а чувства — его планеты."
]

riddles = {
    "Я самая большая планета Солнечной системы, у меня есть кольца и множество спутников. Кто я?": "Юпитер",
    "Я красная планета и мечта колонизаторов. Кто я?": "Марс",
    "Я вторая планета от Солнца и очень горячая. Кто я?": "Венера",
    "Великан-тяжеловес мечет молнии с небес, полосат он словно кот. Кто это?": "Юпитер",
    "Я окружена кольцами и считаюсь самой красивой планетой. Кто я?": "Сатурн"
}

users_riddles = {}

def keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton("🪐 Факт о космосе"),
        types.KeyboardButton("🌟 Цитата"),
        types.KeyboardButton("🛰 Загадка")
    )
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Космический бот 🚀\nВыберите действие:", reply_markup=keyboard())
    save_stats(message.chat.id, message.from_user.username, message.from_user.first_name, "start", "/start")

@bot.message_handler(content_types=["text"])
def handle(message):
    uid = message.chat.id
    text = message.text.strip()

    if text == "🪐 Факт о космосе":
        fact = random.choice(facts)
        bot.send_message(uid, fact)
        save_stats(uid, message.from_user.username, message.from_user.first_name, "fact", fact)

    elif text == "🌟 Цитата":
        quote = random.choice(quotes)
        bot.send_message(uid, quote)
        save_stats(uid, message.from_user.username, message.from_user.first_name, "quote", quote)

    elif text == "🛰 Загадка":
        riddle, answer = random.choice(list(riddles.items()))
        users_riddles[uid] = answer
        bot.send_message(uid, riddle)
        save_stats(uid, message.from_user.username, message.from_user.first_name, "riddle_sent", riddle, answer)

    elif uid in users_riddles:
        answer = users_riddles[uid]
        if text.lower() == answer.lower():
            bot.send_message(uid, "Верно ✅")
        else:
            bot.send_message(uid, f"Неверно ❌ Правильный ответ: {answer}")
        save_stats(uid, message.from_user.username, message.from_user.first_name, "riddle_answer", text, answer)
        users_riddles.pop(uid)

    else:
        bot.send_message(uid, "Используй кнопки ниже", reply_markup=keyboard())
        save_stats(uid, message.from_user.username, message.from_user.first_name, "unknown", text)

if __name__ == "__main__":
    print_analytics()
    bot.polling(none_stop=True) 