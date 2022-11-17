import random
from telebot import types, apihelper
import time
from telebot import TeleBot
import sqlite3 as sql


"""в случае всех вопросов пишите в тг ;)"""
TOKEN = '? писать в телеграме за токеном или вставить свой'
bot = TeleBot(token=TOKEN)
user_tag_id = dict()
db = sql.connect('usernames.db', check_same_thread=False)
query = db.cursor()
query.execute("""CREATE TABLE IF NOT EXISTS users(
   username TEXT PRIMARY KEY,
   userid INT
   )""")
db.commit()


list_of_answers = ['Какой твой любимый цвет?', 'Какое твое любимое время года и почему?', 'А зачем ты здесь?', 'Осьминог или кальмар?', 'Слетал бы на параплане бесплатно?', 'Telegram или VK?']
id_stickers = ['CAACAgIAAxkBAAEGdR5jdpCJCRmxG8gLl48JU-OX0MArXgACIBkAAibr2Uu9OlfgLz3jZisE', 'CAACAgIAAxkBAAEGdSBjdpL-CerCsVARz5zMRvL79IHg7gAC5xUAAias6UpzCM56zo89MSsE',
               'CAACAgIAAxkBAAEGdSJjdpMc0r-zEdnNuVvg635_pvfcUgACVxkAAqlX8EpUfCZDs5zAkysE', 'CAACAgIAAxkBAAEGdSRjdpM0PuRbcv2524yrqLpKs-VS0gACYxoAAvv4mUvQ32lUgqW8XCsE',
               'CAACAgIAAxkBAAEGdSZjdpNnEL0XNYlQ7bm4XJc5m3zooAACIBkAAibr2Uu9OlfgLz3jZisE', 'CAACAgIAAxkBAAEGdShjdpNqhO2bq39PT3eO_25tmHJTQQACBRYAAvGkoUuzl4gkVZltvysE',
               'CAACAgIAAxkBAAEGdSpjdpOGGzVF0ZhkHybgXPJrGD997gACKBcAAoT8yUoYstubMepK0CsE', 'CAACAgIAAxkBAAEGdSxjdpOIvmTx13qmU8iaZ3r7MB3N8wACDxUAAsn5yUriAz6Jj7HzUCsE',
               'CAACAgIAAxkBAAEGdS5jdpOd72MKqab53MOKD7Jv51TJpgAC7hUAAoE-GUsuYVl42pj8PSsE', 'CAACAgIAAxkBAAEGdTBjdpOpZn3NnLcdPdl4wMaC7oqghwACUxsAAjZ0eUvs4vgvpRQVMisE']

@bot.message_handler(commands=["start", "info"])
def start_message(message: types.Message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Привет! Это бот, который может тебя стереть отсюда, дать власть в чате или помочь с администрированием, вся инфа в команде ниже!\n'
                                          '/info - ознакомительная инфа')
    elif message.text[:5] == '/info':
        bot.send_message(message.chat.id, f"Если ты админ, то можешь: \n1) /admin - сделать админом человека в чате ответом на его сообщение\n"+
                         f"2) /ban - ответом на сообщение забанить участника\n3) ban @username - забанить человека по тегу в чате, т.е. исключить\n"+
                         f"4) /mute - запретить писать человеку сообщения на 1 час\n5) /unmute - вытащить человека из мута и разрешить писать в чате, если срок мута не истек.\n"+
                         f"Команды 4 и 5 должны быть ответом на сообщение участника, иначе не сработает!\n "+
                         f"6) /leavebot - бот покинет чат\nЕсли ты не админ, то для тебя:\n7) /pon - узнай, какой ты сегодня обезьяний пон (для всех участников)")


@bot.message_handler(commands=["stat"])
def start_message(message: types.Message):
    if message.text == '/stat':
        bot.send_message(message.chat.id, f"<b>Статистика</b>\n\nВсего пользователей в чате: {bot.get_chat_member_count(message.chat.id)},"
                                          f"\nВсего администраторов в чате: {len(bot.get_chat_administrators(message.chat.id))}", parse_mode='html')


@bot.message_handler(content_types=['new_chat_members'])
def add_to_dict(message: types.Message):
    member = message.new_chat_members[0]
    username = member.username
    user_tag_id[member.username] = member.id
    bot.send_message(message.chat.id, f'Привет, @{username}! Ответь на вопрос: \n{random.choice(list_of_answers)}')
    query.execute("""INSERT INTO users VALUES(?, ?);""", (username, member.id))
    db.commit()


@bot.message_handler(func=lambda x: x.text[:6] == '/admin')
def make_admin(message: types.Message):
    if not message.reply_to_message:
        return bot.send_message(message.chat.id, "Команда применима к ответу на сообщение! Попробуйте еще раз!")
    try:
        bot.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.send_message(message.chat.id, f'Пользователь {message.reply_to_message.from_user.id} теперь админ!')
    except apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, f"К сожалению, сейчас бот не может сделать этого человека администратором.")


@bot.message_handler(commands=["ban"])
def ban_chat_member(message: types.Message):
    if message.reply_to_message:
        bot.send_message(text=f'Пользователь {message.reply_to_message.from_user.id} был забанен!', chat_id=message.chat.id)
        bot.ban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id, until_date=time.time()+10)


@bot.message_handler(content_types=["text"], func=lambda x: x.text[:5] == 'ban @')
def ban_chat_member(message: types.Message):
    id = message.text.split()[1][1:]
    query.execute("SELECT * FROM users WHERE username=?", (id,))
    db.commit()
    x = query.fetchone()
    try:
        bot.ban_chat_member(chat_id=message.chat.id, user_id=x[1])
        bot.send_message(text=f'Пользователь @{id} был забанен!', chat_id=message.chat.id)
    except apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, "Такого пользователя в чате нет!")


@bot.message_handler(commands=["unban"])
def ban_chat_member(message: types.Message):
    if message.text == '/unban':
        bot.send_message(text=f'Пользователь {message.reply_to_message.from_user.id} был разбанен!', chat_id=message.chat.id)
        bot.unban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)


@bot.message_handler(commands=["mute"])
def mute(message):
    time2 = 3600
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=time.time() + time2)
    bot.send_message(message.chat.id, f'Пользователь был замьючен на {time2 // 60} минут!', reply_to_message_id=message.message_id)


@bot.message_handler(commands=["pon"])
def pon(message: types.Message):
    bot.send_message(message.chat.id, 'Ты сегодня')
    bot.send_sticker(message.chat.id, random.choice(id_stickers))


@bot.message_handler(commands=["unmute"])
def mute(message):
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=time.time() + 0.00001)
    bot.send_message(message.chat.id, f'Пользователь вышел из мута!', reply_to_message_id=message.message_id)


@bot.message_handler(commands=["leavebot"])
def leave_chat(message: types.Message):
    print('advknokjef')
    participant = bot.get_chat_member(message.chat.id, message.from_user.id)
    if participant.status != 'creator' and participant.status != 'administrator':
        bot.send_message(message.chat.id, 'Кыш-кыш, не трогай бота, это могут только админы!')
        return
    try:
        bot.leave_chat(message.chat.id)
    except apihelper.ApiTelegramException:
        pass


bot.infinity_polling()
