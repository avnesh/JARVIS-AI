import requests
import wikipedia
import pywhatkit as kit
from email.message import EmailMessage
import smtplib
import os
import pyttsx3
import threading

from constants import (
    EMAIL,
    PASSWORD,
    SMTP_URL,
    SMTP_PORT,
    NEWS_FETCH_API_URL,
    NEWS_FETCH_API_KEY,
    NEWS_SEARCH_URL,
    WEATHER_FORECAST_API_KEY,
    WEATHER_CURRENT_URL
)

def speak(text):
    # Use pyttsx3 for reliable, offline, and snappy voice (Iron Man style)
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170) # Speed it up slightly
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Voice Error: {e}")
    pass
    
def find_my_ip():
    try:
        ip_address = requests.get('https://api64.ipify.org?format=json').json()
        return ip_address["ip"]
    except:
        return "Unknown"


def search_on_wikipedia(query):
    try:
        results = wikipedia.summary(query, sentences=2)
        return results
    except:
        return "I couldn't find that on Wikipedia."


def search_on_google(query):
    kit.search(query)


def youtube(video):
    kit.playonyt(video)


def send_email(receiver_add, subject, message):
    try:
        email = EmailMessage()
        email['To'] = receiver_add
        email['Subject'] = subject
        email['From'] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP(SMTP_URL, SMTP_PORT)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(e)
        return False


def get_news(query="India"):
    news_headline = []
    try:
        # Use NEWS_SEARCH_URL if available (User preference)
        if NEWS_SEARCH_URL:
            # Replace {QUERY} with actual query or default
            url = NEWS_SEARCH_URL.replace("{QUERY}", query)
            result = requests.get(url).json()
        else:
            # Fallback to old keys/params
            result = requests.get(
                NEWS_FETCH_API_URL,
                params={
                    "country":"in",
                    "category":"general",
                    "apiKey": NEWS_FETCH_API_KEY
                },
            ).json()
            
        articles = result.get("articles", [])
        for article in articles:
            news_headline.append(article["title"])
        return news_headline[:6]
    except Exception as e:
        print(f"News Error: {e}")
        return ["I could not fetch the news at this time."]


def weather_forecast(city):
    try:
        if WEATHER_CURRENT_URL:
            # Use user-provided template: https://api.weatherapi.com/...&q={CITY}
            url = WEATHER_CURRENT_URL.replace("{CITY}", city)
            res = requests.get(url).json()
        else:
            # Fallback to constructed URL
            api_key = WEATHER_FORECAST_API_KEY
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no"
            res = requests.get(url).json()
            
        if "error" in res:
            raise Exception(res["error"]["message"])
            
        weather = res["current"]["condition"]["text"]
        temp = res["current"]["temp_c"]
        feels_like = res["current"]["feelslike_c"]
        return weather, f"{temp}°C", f"{feels_like}°C"
    except Exception as e:
        print(f"Weather Error: {e}")
        return "Unknown", "N/A", "N/A"
