import os
from dotenv import dotenv_values

"""
weather_api_key = os.getenv("WEATHER_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
"""

env = dotenv_values(".env")
weather_api_key = env["WEATHER_API_KEY"]
telegram_bot_token = env["TELEGRAM_BOT_TOKEN"]
