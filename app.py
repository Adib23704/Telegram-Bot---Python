import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ.get('TOKEN')
API_KEY = os.environ.get('API_KEY')

def get_temperature(location):
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?key={API_KEY}&contentType=json&include=current&unitGroup=us'
    response = requests.get(url)
    return response

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

async def location(update, context):
    response = get_temperature(update.message.text)
    if response.status_code == 200:
        data = response.json()
        temperature_f = data['currentConditions']['temp']

        keyboard = [[InlineKeyboardButton("Show in Celsius", callback_data=f"celsius {temperature_f:.1f} {update.message.text}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"The current temperature of {update.message.text} is {temperature_f}°F", reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error! Please enter a valid location name:")

async def button(update, context):
    query = update.callback_query
    data = query.data.split()

    if data[0] == "celsius":
        temperature_f = float(data[1])
        temperature_c = fahrenheit_to_celsius(temperature_f)
        keyboard = [[InlineKeyboardButton("Show in Fahrenheit", callback_data=f"fahrenheit {temperature_c:.1f} {data[2]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"The current temperature of {data[2]} is {temperature_c:.1f}°C", reply_markup=reply_markup)
    elif data[0] == "fahrenheit":
        temperature_c = float(data[1])
        temperature_f = celsius_to_fahrenheit(temperature_c)
        keyboard = [[InlineKeyboardButton("Show in Celsius", callback_data=f"celsius {temperature_f:.1f} {data[2]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"The current temperature of {data[2]} is {temperature_f:.1f}°F", reply_markup=reply_markup)

async def start_with_keyboard(update, context):
    keyboard = [["/start"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! Please enter a location name:", reply_markup=reply_markup)

updater = Application.builder().token(TOKEN).build()

if updater.bot.get_me is None:
    print("Bot initialization failed")
    exit(1)
else:
    print("Bot initialized successfully")

start_handler = CommandHandler('start', start_with_keyboard)
location_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, location)
button_handler = CallbackQueryHandler(button)

updater.add_handler(start_handler)
updater.add_handler(location_handler)
updater.add_handler(button_handler)

updater.run_polling(allowed_updates=Update.ALL_TYPES)