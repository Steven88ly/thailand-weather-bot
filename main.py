# This script uses OpenWeatherMap (fallback for TMD) and GitHub Actions to send daily emails
# Replace placeholders with your real info before use

import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- CONFIG ---
OPENWEATHER_API_KEY = "your_openweather_api_key"
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
RECIPIENTS = ["chrisforlini1@gmail.com", "steven88ly@gmail.com"]

LOCATIONS = {
    "Phuket":  "8.0000,98.2934",
    "Krabi":   "8.0863,98.9063"
}

DAYS_TO_CHECK = {
    "Phuket": ["2025-05-21", "2025-05-22", "2025-05-23", "2025-05-24"],
    "Krabi": ["2025-05-25", "2025-05-26", "2025-05-27"]
}

# --- FETCH WEATHER ---
def get_forecast(city, latlon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latlon.split(',')[0]}&lon={latlon.split(',')[1]}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

# --- ANALYZE FORECAST ---
def analyze_rain(forecast_data, dates):
    rain_days = {}
    for entry in forecast_data['list']:
        dt_txt = entry['dt_txt']
        date = dt_txt.split(' ')[0]
        if date in dates:
            rain = entry.get('rain', {}).get('3h', 0)
            if rain > 0:
                rain_days[date] = rain_days.get(date, 0) + 1

    rainy_days = [day for day, count in rain_days.items() if count >= 2]
    return len(rainy_days), rain_days

# --- FORMAT EMAIL ---
def format_report():
    message = f"\U0001F3D6️ Thailand Weather Update – {datetime.today().strftime('%b %d')}\n\n"
    for city, latlon in LOCATIONS.items():
        forecast = get_forecast(city, latlon)
        rainy_count, detail = analyze_rain(forecast, DAYS_TO_CHECK[city])

        message += f"\n\U0001F4CD {city} ({', '.join(DAYS_TO_CHECK[city])}):\n"
        for date in DAYS_TO_CHECK[city]:
            blocks = detail.get(date, 0)
            icon = "\u2614\ufe0f" if blocks >= 2 else ("\u2600\ufe0f" if blocks == 0 else "\u26C5")
            message += f"- {date}: {icon} ({blocks} rainy blocks)\n"

        if rainy_count >= 2:
            message += "\u26A0\ufe0f 2+ days show high rain chance. Plan B might be necessary.\n"
        else:
            message += "\u2705 Looks manageable. No immediate need to switch plans.\n"
    return message

# --- SEND EMAIL ---
def send_email(body):
    msg = MIMEText(body)
    msg["Subject"] = "Daily Thailand Weather Update"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(RECIPIENTS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, RECIPIENTS, msg.as_string())

# --- MAIN ENTRY ---
if __name__ == "__main__":
    report = format_report()
    send_email(report)
