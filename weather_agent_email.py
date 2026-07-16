import smtplib
import schedule
import time
import requests
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
SENDER_EMAIL = "write the mail you want to send from"
RECEIVER_EMAIL = "write the mail you want ot send to"
EMAIL_PASSWORD = "write here the email app password" 

# --- FUNCTIONS ---

def get_weather_data():
    """משיכת נתוני טמפרטורה ולחות מ-Netanya"""
    #this version is for Netanya, Israel but you can change the api through meteo website for your city
    url = "https://api.open-meteo.com/v1/forecast?latitude=32.3276&longitude=34.856&hourly=temperature_2m,relative_humidity_2m&forecast_days=1"
    response = requests.get(url).json()
    return response['hourly']['time'], response['hourly']['temperature_2m'], response['hourly']['relative_humidity_2m']

def create_weather_graph(times, temps, humidity):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    short_times = [t.split('T')[1] for t in times[::3]]
    
    # גרף טמפרטורה
    ax1.plot(short_times, temps[::3], color='red', marker='o', label='Temp (°C)')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp (°C)', color='red')
    
    # --- כאן מתבצע השינוי ---
    # מציאת הערך המקסימלי בטמפרטורה והוספת 1 מעלה למרווח
    max_temp = max(temps)
    ax1.set_ylim(min(temps) - 2, max_temp + 1)
    # --------------------------
    
    # גרף לחות
    ax2 = ax1.twinx()
    ax2.plot(short_times, humidity[::3], color='blue', marker='x', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)', color='blue')
    ax2.set_ylim(0, 100) # ללחות הגיוני להגביל בין 0 ל-100
    
    plt.title("Netanya Weather Forecast")
    plt.savefig('weather_temp.png')
    plt.close()

    # הוספת טקסט על התמונה
    img = Image.open('weather_temp.png')
    draw = ImageDraw.Draw(img)
    
    # הגדרת פרטים
    date_str = datetime.now().strftime('%Y-%m-%d')
    source_str = "Source: Open-Meteo"
    
    # כתיבת הטקסט בפינות (x, y)
    draw.text((10, 10), date_str, fill="black") # פינה שמאלית עליונה
    draw.text((img.width - 120, 10), source_str, fill="black") # פינה ימנית עליונה
    
    img.save('weather.png') # זו התמונה הסופית שתישלח

def send_email_with_graph():
    times, temps, humidity = get_weather_data()
    create_weather_graph(times, temps, humidity)

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"Daily Weather & Humidity: {datetime.now().strftime('%Y-%m-%d')}"
    
    body = "Hello! Here is the daily temperature and humidity forecast graph for Netanya."
    msg.attach(MIMEText(body, 'plain'))

    with open('weather.png', 'rb') as f:
        img_data = f.read()
    
    image = MIMEImage(img_data, name='weather.png')
    msg.attach(image)

    server = smtplib.SMTP('smtp.gmail.com', 587, local_hostname="localhost")
    server.starttls()
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    print("Weather and Humidity report sent successfully.")

# --- SCHEDULER ---
schedule.every().day.at("05:00").do(send_email_with_graph)

print("Weather Agent is running. Waiting for 05:00...")

while True:
    schedule.run_pending()
    time.sleep(60)