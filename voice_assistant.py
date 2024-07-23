import speech_recognition as sr
import pyttsx3
import spacy
import requests
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Initialize SpaCy
nlp = spacy.load('en_core_web_sm')

# Your OpenWeatherMap API key
WEATHER_API_KEY = 'your_correct_openweathermap_api_key_here'

# Email credentials
EMAIL_ADDRESS = 'blake18465@gmail.com'
EMAIL_PASSWORD = 'Bigblockboi3000!'

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to listen to a command
def listen_to_command():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio_data)
            print(f"Recognized command: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

# Function to speak a response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to get weather information
def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    print(f"Request URL: {url}")  # Debugging
    print(f"Response Status Code: {response.status_code}")  # Debugging

    if response.status_code == 200:
        data = response.json()
        print(f"API Response: {data}")  # Debugging
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
    else:
        print(f"Error Response: {response.text}")  # Debugging
        return "I couldn't retrieve the weather information right now."

# Function to set a reminder
def set_reminder(reminder_text, reminder_time):
    try:
        # Validate time format
        parsed_time = datetime.strptime(reminder_time, '%H:%M')
        formatted_time = parsed_time.strftime('%H:%M')
        
        def reminder_task():
            speak(f"Reminder: {reminder_text}")
            print(f"Reminder: {reminder_text}")

        schedule.every().day.at(formatted_time).do(reminder_task)
        return f"Reminder set for {formatted_time}"
    except ValueError:
        return "Invalid time format. Please use HH:MM format."

# Function to perform a web search using DuckDuckGo
def perform_web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
    response = requests.get(url)
    print(f"Request URL: {url}")  # Debugging
    print(f"Response Status Code: {response.status_code}")  # Debugging

    if response.status_code == 200:
        data = response.json()
        print(f"API Response: {data}")  # Debugging
        if 'AbstractText' in data and data['AbstractText']:
            return data['AbstractText']
        else:
            return "I couldn't find any results for your query."
    else:
        print(f"Error Response: {response.text}")  # Debugging
        return "I couldn't perform the web search right now."

# Function to send an email
def send_email(recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, recipient, text)
        server.quit()

        return f"Email sent to {recipient}"
    except Exception as e:
        return f"Failed to send email. Error: {e}"

# Function to process the command using advanced NLP
def process_command(command):
    doc = nlp(command)
    print(f"Tokens: {[token.text for token in doc]}")
    print(f"Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")

    if 'weather' in command:
        city = None
        for ent in doc.ents:
            if ent.label_ == 'GPE':  # Geopolitical entity
                city = ent.text
                break
        if city:
            return get_weather(city)
        else:
            return "Please specify the city you want the weather information for."
    elif 'time' in command:
        now = datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}"
    elif 'name' in command:
        return "My name is Voice Assistant."
    elif 'joke' in command:
        return "Why don't scientists trust atoms? Because they make up everything!"
    elif 'remind me' in command.lower():
        reminder_text = command.lower().split("remind me to")[1].strip()
        if 'at' in reminder_text:
            reminder_text, reminder_time = reminder_text.split('at')
            reminder_text = reminder_text.strip()
            reminder_time = reminder_time.strip()
            return set_reminder(reminder_text, reminder_time)
        else:
            return "Please specify the time for the reminder."
    elif 'search for' in command.lower():
        search_query = command.lower().split("search for")[1].strip()
        return perform_web_search(search_query)
    elif 'send email to' in command.lower():
        parts = command.lower().split("send email to")
        if len(parts) > 1:
            details = parts[1].strip().split("subject")
            if len(details) > 1:
                recipient = details[0].strip()
                subject_body = details[1].strip().split("body")
                if len(subject_body) > 1:
                    subject = subject_body[0].strip()
                    body = subject_body[1].strip()
                    return send_email(recipient, subject, body)
                else:
                    print(f"Subject Body Parsing Failed: {subject_body}")  # Debugging
        else:
            print(f"Email Parsing Failed: {parts}")  # Debugging
        return "Please specify the recipient, subject, and body of the email."
    elif 'stop listening' in command.lower():
        return "Stopping the assistant. Goodbye!"
    else:
        return "I'm not sure how to respond to that. Can you try asking something else?"

if __name__ == "__main__":
    try:
        while True:
            command = listen_to_command()
            if command:
                response = process_command(command)
                speak(response)
                if 'stop listening' in command.lower():
                    break
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Voice assistant terminated by user.")