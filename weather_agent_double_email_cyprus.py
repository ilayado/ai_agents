import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image, ImageDraw
import schedule
import time

# --- הגדרות ---
SENDER_EMAIL = "ilayadonyahu12@gmail.com"
EMAIL_PASSWORD = "bfgkynnisrsyvqdb"
RECIPIENTS = ["eadonyahu@gmail.com", "muehlst@hotmail.com"]

def get_weather_data():
    # קואורדינטות של איה נאפה, קפריסין
    url = "https://api.open-meteo.com/v1/forecast?latitude=34.98&longitude=34.00&hourly=temperature_2m,relative_humidity_2m&forecast_days=1"
    try:
        # הוספנו timeout=10, זה אומר לפייתון להמתין 10 שניות ולוותר אם אין תשובה
        response = requests.get(url, timeout=10).json()
        return response['hourly']['time'], response['hourly']['temperature_2m'], response['hourly']['relative_humidity_2m']
    except Exception as e:
        print(f"שגיאה במשיכת נתוני מזג האוויר: {e}")
        # מחזירים ערכים ריקים כדי למנוע קריסה של התוכנית
        return [], [], []
    
def create_weather_graph(times, temps, humidity):
    fig, ax1 = plt.subplots(figsize=(12, 6)) # הגדלתי קצת את הגרף שיהיה מקום למספרים
    short_times = [t.split('T')[1] for t in times[::3]]
    temps_subset = temps[::3]
    hum_subset = humidity[::3]
    
    # --- ציר טמפרטורה (אדום) ---
    color_temp = 'red'
    ax1.plot(short_times, temps_subset, color=color_temp, marker='o', label='Temp (°C)')
    ax1.set_ylim(min(temps) - 2, max(temps) + 3) # הוספתי עוד קצת מקום למעלה לטקסט
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temp (°C)', color=color_temp)
    ax1.tick_params(axis='y', labelcolor=color_temp)
    
    # הוספת ערכי הטמפרטורה מעל הנקודות
    for x, y in zip(short_times, temps_subset):
        ax1.text(x, y + 0.3, f'{y}', color=color_temp, fontsize=10, ha='center')

    # --- ציר לחות (כחול) ---
    ax2 = ax1.twinx()
    color_hum = 'blue'
    ax2.plot(short_times, hum_subset, color=color_hum, marker='x', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)', color=color_hum)
    ax2.tick_params(axis='y', labelcolor=color_hum)
    
    min_hum = min(humidity)
    max_hum = max(humidity)
    ax2.set_ylim(min_hum - 5, max_hum + 10) # הוספתי מקום למעלה לטקסט
    
    # הוספת ערכי הלחות מעל הנקודות
    for x, y in zip(short_times, hum_subset):
        ax2.text(x, y + 1, f'{y}', color=color_hum, fontsize=10, ha='center')
    
    plt.title("Ayia Napa Weather Forecast")
    plt.tight_layout()
    plt.savefig('weather_temp.png')
    plt.close()

    # הוספת תאריך ומקור עם Pillow
    img = Image.open('weather_temp.png')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), datetime.now().strftime('%Y-%m-%d'), fill="black")
    draw.text((img.width - 120, 10), "Source: Open-Meteo", fill="black")
    img.save('weather.png')

def send_email_with_graph():
    times, temps, humidity = get_weather_data()
    create_weather_graph(times, temps, humidity)

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['Subject'] = "Cyprus Daily Weather Forecast"
    
    msg.attach(MIMEText("בוקר טוב! מצורפת התחזית היומית לקפריסין.", 'plain'))

    with open('weather.png', 'rb') as f:
        img_data = f.read()
    
    image = MIMEImage(img_data, name="weather.png")
    msg.attach(image)

    # --- התיקון כאן ---
    # אנחנו מגדירים לשרת שם מחשב פשוט באנגלית כדי למנוע את שגיאת הקידוד
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo(name='localhost') # <--- הוסף את השורה הזו
    server.starttls()
    server.ehlo(name='localhost') # <--- וגם כאן
    # ------------------
    
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
    server.quit()
    print(f"המייל נשלח בהצלחה ל-{', '.join(RECIPIENTS)}")

# --- לופ הפעלה ---
# להרצה כל יום ב-05:00:
schedule.every().day.at("05:00").do(send_email_with_graph)

# (אופציונלי: להרצה כל דקה לצורך בדיקה, תוריד את ההערה מהשורה הבאה ותעיר את השורה הקודמת)
# schedule.every(1).minutes.do(send_email_with_graph)

print("הבוט פעיל. ממתין לשעה 05:00...")

while True:
    schedule.run_pending()
    time.sleep(60)