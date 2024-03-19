#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import json
import logging
import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext.filters import Text

from config import weather_api_key, telegram_bot_token

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

user_states = {}

async def get_weather(city_name: str):
    api_key = weather_api_key
    base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

    response = requests.get(base_url)
    if response.status_code == 404:
        return {"status": "error"}
    else:
        data = response.json()
        temp = {
            "celcius": round(data["main"]["temp"] - 273.15, 2),
            "fahrenheit": round((data["main"]["temp"] - 273.15) * 9/5 + 32, 2),
            "status": "success"
        }
        return temp

from telegram import ReplyKeyboardMarkup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with a button labeled "/start" under the message field."""

    user_states[update.message.from_user.id] = True

    # Create a reply keyboard with the "/start" button
    keyboard = [["/start"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Send a message with the reply keyboard
    await update.message.reply_text("Write a city name to get the weather.", reply_markup=reply_markup)

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the message received after sending the city name."""

    user_id = update.message.from_user.id
    if user_id in user_states and user_states[user_id] == True:
        city_name = update.message.text
        # Process the city name here to get weather information
        # For example, you can call a weather API to get the weather for the specified city
        weather = await get_weather(city_name)

        if weather.get("status") == "error":
            await update.message.reply_text("City not found. Please enter a valid city name.")
            return

        await update.message.reply_text(f"You entered the city: {city_name}. Now I will retrieve the weather for this city.")

        keyboard = [
            [InlineKeyboardButton("Show in Fahrenheit", callback_data=json.dumps({'parameter': 'fahrenheit', 'value': weather['celcius'], 'city': city_name}))],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"The temperature in {city_name} is {weather['celcius']}°C", reply_markup=reply_markup)

        # Reset user state
        del user_states[user_id]
    else:
        await update.message.reply_text("Please start by typing /start to initiate the process.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button press to toggle temperature units."""
    query = update.callback_query
    data = json.loads(query.data)
    print(data)
    if data.get("parameter") == "fahrenheit":
        # convert the data to a farhenheit value
        fahrenheit = float("{:.2f}".format((data.get('value') * 9/5) + 32))


        keyboard = [
            [InlineKeyboardButton("Show in Celcius", callback_data=json.dumps({'parameter': 'celcius', 'value': fahrenheit, 'city': data.get('city')}))],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Update the message with temperature in Fahrenheit
        await query.edit_message_text(f"The temperature in {data.get('city')} is {fahrenheit}°F", reply_markup=reply_markup)

    if data.get("parameter") == "celcius":

        celcius = float("{:.2f}".format((data.get('value') - 32) * 5/9))

        keyboard = [
            [InlineKeyboardButton("Show in Fahrenheit", callback_data=json.dumps({'parameter': 'fahrenheit', 'value': celcius, 'city': data.get('city')}))],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Update the message with temperature in Fahrenheit
        await query.edit_message_text(f"The temperature in {data.get('city')} is {celcius}°C", reply_markup=reply_markup)

    # Answer the callback query
    await query.answer()
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()