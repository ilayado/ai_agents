import telegram
import asyncio
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image, ImageDraw
import schedule
import time

# --- הגדרות ---
TOKEN = "write your botFather token in telegram"
CHAT_ID = "write your chat ID"

def get_weather_data():
    #this version is for Netanya, Israel but you can change the api through meteo website for your city
    url = "https://api.open-meteo.com/v1/forecast?latitude=32.3276&longitude=34.856&hourly=temperature_2m,relative_humidity_2m&forecast_days=1"
    response = requests.get(url).json()
    return response['hourly']['time'], response['hourly']['temperature_2m'], response['hourly']['relative_humidity_2m']

def create_weather_graph(times, temps, humidity):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    short_times = [t.split('T')[1] for t in times[::3]]
    
    ax1.plot(short_times, temps[::3], color='red', marker='o', label='Temp (°C)')
    ax1.set_ylim(min(temps) - 2, max(temps) + 1)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp (°C)', color='red')
    
    ax2 = ax1.twinx()
    ax2.plot(short_times, humidity[::3], color='blue', marker='x', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)', color='blue')
    ax2.set_ylim(0, 100)
    
    plt.title("Netanya Weather Forecast")
    plt.savefig('weather_temp.png')
    plt.close()

    # הוספת תאריך ומקור עם Pillow
    img = Image.open('weather_temp.png')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), datetime.now().strftime('%Y-%m-%d'), fill="black")
    draw.text((img.width - 120, 10), "Source: Open-Meteo", fill="black")
    img.save('weather.png')

async def send_to_telegram():
    times, temps, humidity = get_weather_data()
    create_weather_graph(times, temps, humidity)
    
    bot = telegram.Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="בוקר טוב! הנה תחזית מזג האוויר להיום בנתניה ☀️")
    with open('weather.png', 'rb') as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=photo)
    print("Weather and Humidity report sent successfully.")

# --- לופ הפעלה ---
def job():
    asyncio.run(send_to_telegram())

schedule.every().day.at("05:00").do(job)
# schedule.every(1).minutes.do(job)

print("Weather Agent is running. Waiting for 05:00...")

while True:
    schedule.run_pending()
    time.sleep(60)