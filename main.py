## Скрипт взят с https://t.me/BlackCloudSoft ##

import logging
import asyncio
from pydoc import html
import random
import sqlite3
import string

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.exceptions
from aiogram.types.message import ContentTypes

#конфиг
BOT_TOKEN = '8709666507:AAHu8qEf0CAc8uyQsd5OEqxQtjkVPjwRbm0'#Токен бота
ADMIN_LIST = [8795006636] #Id админа
from database import dbworker

db = dbworker('db.db')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())

logging.basicConfig(filename="all_log.log", level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)

fh = logging.FileHandler("warning_log.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)


warning_log.addHandler(fh)

@dp.message_handler(commands=['start'],state='*')
async def start(message : types.Message, state: FSMContext):

    await state.finish()

    button_search = KeyboardButton('Начать поиск🔍')
    button_info_project = KeyboardButton('Правила📖')
    count_users = KeyboardButton(f'В боте {int(db.count_user() * 1.5)} пользователей 👤')
    mark_menu = ReplyKeyboardMarkup(resize_keyboard=True).add()
    mark_menu.add(button_search,button_info_project)
    mark_menu.add(count_users)

    await bot.send_sticker(chat_id=message.from_user.id,
                           sticker=r"CAACAgQAAxkBAAEEkZ1iaFWceel2GJcD_r7MYPl1a5rROwACvQkAAnpcEVM6alQk5njq3yQE")
    await bot.send_message(message.chat.id, f'<b>👋 Привет! Это Анонимный чат Телеграма.</b>\n'
                                            f'<i>Тут можно общаться 1 на 1 со случайными собеседниками.</i>\n\n'
                                            f'<b>📖 В чате есть правила поведения, которые нужно соблюдать.</b>\n'
                                            f'<i>Нельзя спамить, продвигать свои услуги, оскорблять собеседников.</i>\n\n'
                                            f'<b>📋 Подробнее правила можно прочитать тут:</b>\n'
                                            f'/rules или нажать кнопку "Правила📖"\n\n'
                                            f'<b>🔎 Работает бот очень просто:</b> вы жмете кнопку поиска или используете команду /search и бот находит вам собеседника.'
                                            f'<i>Удачного общения! Будьте вежливы к собеседникам.</i> t.me/BlackCloudSoft',reply_markup=mark_menu, parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['rules'],state='*')
@dp.message_handler(lambda message : message.text == 'Правила📖')
async def rules(message : types.Message):
    await message.answer(f'<b>📌Правила общения</b>\n'
                         f'<i>1. Любые упоминания психоактивных веществ. (наркотиков)\n'
                         f'2. Детская порнография. ("ЦП")\n3. Мошенничество. (Scam)\n'
                         f'4. Любая реклама, спам.\n'
                         f'5. Продажи чего либо. (например - продажа интимных фотографий, видео)\n'
                         f'6. Любые действия, нарушающие правила Telegram.\n'
                         f'7. Оскорбительное поведение.\n'
                         f'8. Обмен, распространение любых 18+ материалов\n\n</i>', parse_mode=types.ParseMode.HTML)

@dp.message_handler(commands=['search'],state='*')
@dp.message_handler(lambda message: message.text == 'Начать поиск🔍',state='*')
async def search(message : types.Message):
    try:
        if(not db.user_exists(message.from_user.id)):
            db.add_user(message.from_user.username,message.from_user.id)

        male = KeyboardButton('🙎‍♂️ Парня')
        wooman = KeyboardButton('🙍‍♀️ Девушку')
        back = KeyboardButton('🚫 Отменить поиск')
        sex_menu = ReplyKeyboardMarkup(resize_keyboard=True).add()
        sex_menu.add(male,wooman)
        sex_menu.add(back)
        
        await bot.send_sticker(chat_id=message.from_user.id,
                           sticker=r"CAACAgIAAxkBAAEEkZViaFU0G8DjNZCIvxEDdhmtRsBnTwACOAsAAk7kmUsysUfS2U-M0CQE")
        await message.answer('<b>Выбери пол собеседника!\nКого будем искать для тебя 🙍‍♀️/🙎‍♂️</b>',reply_markup=sex_menu, parse_mode=types.ParseMode.HTML)
    except Exception as e:
        warning_log.warning(e)

class Chating(StatesGroup):
	msg = State()

@dp.message_handler(lambda message: message.text == '🙎‍♂️ Парня' or message.text == '🙍‍♀️ Девушку',state='*')
async def chooce_sex(message : types.Message, state: FSMContext):
    ''' Выбор пола для поиска '''
    try:
        if db.queue_exists(message.from_user.id):
            db.delete_from_queue(message.from_user.id)
        if message.text == '🙎‍♂️ Парня':
            db.edit_sex(True,message.from_user.id)
            db.add_to_queue(message.from_user.id,True)
        elif message.text == '🙍‍♀️ Девушку':
            db.edit_sex(False,message.from_user.id)
            db.add_to_queue(message.from_user.id,False)
        else:
            db.add_to_queue(message.from_user.id,db.get_sex_user(message.from_user.id)[0])
        await message.answer('Ищем для вас человечка.. 🔍')

        stop = KeyboardButton('🚫 Остановить диалог')
        menu_msg = ReplyKeyboardMarkup(resize_keyboard=True).add()
        menu_msg.add(stop)

        while True:
            await asyncio.sleep(0.5)
            if db.search(db.get_sex_user(message.from_user.id)[0]) != None:
                try:
                    db.update_connect_with(db.search(db.get_sex_user(message.from_user.id)[0])[0],message.from_user.id)
                    db.update_connect_with(message.from_user.id,db.search(db.get_sex_user(message.from_user.id)[0])[0])
                    break
                except Exception as e:
                    print(e)
        while True:
            await asyncio.sleep(0.5)
            if db.select_connect_with(message.from_user.id)[0] != None:
                break
        try:
            db.delete_from_queue(message.from_user.id)
            db.delete_from_queue(db.select_connect_with(message.from_user.id)[0])
        except:
            pass
        await Chating.msg.set()
        await bot.send_message(db.select_connect_with(message.from_user.id)[0],'<b>Нашёл кое-кого для тебя 💕</b>',reply_markup=menu_msg, parse_mode=types.ParseMode.HTML)
        return
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)

## Скрипт взят с https://t.me/BlackCloudSoft ##
@dp.message_handler(content_types=ContentTypes.TEXT)
@dp.message_handler(state=Chating.msg)
async def chating(message : types.Message, state: FSMContext):
    try:
        next = KeyboardButton('➡️Следующий диалог')
        back = KeyboardButton('🚫 Отменить поиск')
        menu_msg_chating = ReplyKeyboardMarkup(resize_keyboard=True).add()
        menu_msg_chating.add(next,back)
        await state.update_data(msg=message.text)

        user_data = await state.get_data()

        if user_data['msg'] == '🏹Отправить ссылку на себя':
            if message.from_user.username == None:
                await bot.send_message(db.select_connect_with_self(message.from_user.id)[0],'Пользователь не заполнил никнейм в настройках телеграма!')
            else:
                await bot.send_message(db.select_connect_with_self(message.from_user.id)[0],'@' + message.from_user.username)
                await message.answer('@' + message.from_user.username)

        elif user_data['msg'] == '🚫 Остановить диалог':
            await message.answer('<b>Диалог остановлен 🤧 Отправьте /search, чтобы начать поиск</b>',reply_markup=menu_msg_chating, parse_mode=ParseMode.HTML)
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],'<b>Диалог остановлен 🤧 Отправьте /search, чтобы начать поиск</b>',reply_markup=menu_msg_chating, parse_mode=ParseMode.HTML)
            db.update_connect_with(None,db.select_connect_with(message.from_user.id)[0])
            db.update_connect_with(None,message.from_user.id)

        elif user_data['msg'] == '➡️Следующий диалог':
            await chooce_sex(message,state)

        elif user_data['msg'] == 'Подбросить монетку🎲':
            coin = random.randint(1,2)

            if coin == 1:
                coin = text(italic('Решка'))
            else:
                coin = text(italic('Орёл'))

            await message.answer(coin,parse_mode=ParseMode.MARKDOWN)
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],coin,parse_mode=ParseMode.MARKDOWN)

        elif user_data['msg'] == 'Назад':
            await start(message,state)
            await state.finish()

        else:
            await bot.send_message(db.select_connect_with(message.from_user.id)[0],user_data['msg'])
            db.log_msg(message.from_user.id,user_data['msg'])
            db.add_count_msg(message.from_user.id)
            await send_to_channel_log(message)

    except aiogram.utils.exceptions.ChatIdIsEmpty:
        await state.finish()
        await start(message,state)
    except aiogram.utils.exceptions.BotBlocked:
        await message.answer('Пользователь вышел из чат бота!')
        await state.finish()
        await start(message,state)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)

@dp.message_handler(content_types=ContentTypes.PHOTO,state=Chating.msg)
async def chating_photo(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен ФОТОГРАФИЯМИ '''
    try:
        await message.photo[-1].download('photo_user/' + str(message.from_user.id) + '.jpg')
        with open('photo_user/' + str(message.from_user.id) + '.jpg','rb') as photo:
            await bot.send_photo(db.select_connect_with(message.from_user.id)[0],photo,caption=message.text)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)

@dp.message_handler(content_types=ContentTypes.STICKER,state=Chating.msg)
async def chating_sticker(message : types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен CТИКЕРАМИ '''
    try:
        await bot.send_sticker(db.select_connect_with(message.from_user.id)[0],message.sticker.file_id)
    except Exception as e:
        warning_log.warning(e)
        await send_to_channel_log_exception(message,e)
    
@dp.message_handler(commands=['back'])
@dp.message_handler(lambda message : message.text == 'Назад',state='*')
async def back(message : types.Message, state: FSMContext):
    ''' Функция для команды back '''
    await state.finish()
    await start(message,state)

#логи в телеграм канал
async def send_to_channel_log(message : types.Message):
    await bot.send_message(-1111111,f'ID - {str(message.from_user.id)}\nusername - {str(message.from_user.username)}\nmessage - {str(message.text)}')

async def send_to_channel_log_exception(message : types.Message,except_name):
    await bot.send_message(-111111111,f'Ошибка\n\n{except_name}')

@dp.message_handler(lambda message: message.text.startswith('/sendmsg_admin'),state='*')
async def admin_send_msg(message : types.Message):
    if message.from_user.id in ADMIN_LIST:
        msg = message.text.split(',')
        await bot.send_message(int(msg[1]),'Cообщение от админа:\n'  + msg[2])
    else:
        await message.answer('Отказано в доступе')

@dp.message_handler()
async def end(message : types.Message):
	'''Функция непредсказумогого ответа'''
	await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /start и /help')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,)
## Скрипт взят с https://t.me/BlackCloudSoft ##