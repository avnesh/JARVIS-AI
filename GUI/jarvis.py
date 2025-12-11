import time
import threading
import keyboard
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
import pyautogui
import subprocess as sp
import webbrowser
import imdb
from kivy.uix import widget,image,label,boxlayout,textinput,floatlayout
from kivy import clock
from constants import SCREEN_HEIGHT,SCREEN_WIDTH,GEMINI_API_KEY,GROQ_API_KEY
from utils import speak,youtube,search_on_google,search_on_wikipedia,send_email,get_news,weather_forecast,find_my_ip
from jarvis_button import JarvisButton
from groq import Groq
import psutil # For System Realism
import platform
from AppOpener import open as app_open, close as app_close
import sys # Needed for stderr patching

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

class Jarvis(floatlayout.FloatLayout):
    def __init__(self, **kwargs):
        super(Jarvis, self).__init__(**kwargs)
        self.volume = 0
        self.volume_history = [0,0,0,0,0,0,0]
        self.volume_history_size = 140
        self.is_listening = False # Prevent overlapping listen threads
        
        # Initialize J.A.R.V.I.S. Memory and Persona
        # Initialize J.A.R.V.I.S. Memory and Persona
        self.conversation_history = [
            {"role": "system", "content": "You are J.A.R.V.I.S., a highly advanced AI assistant. You are helpful, precise, witty, and loyal. You always address the user as 'Sir'. Keep your responses concise and efficient, suitable for a verbal interface. IMPACTFUL INSTRUCTION: If the user provides an incomplete query, ask for clarification. If they follow up, combine it with the previous context. LANGUAGE PROTOCOL: STRICTLY Match the user's language. If the user speaks English, reply in English. If the user speaks Hindi or Hinglish, reply in Hinglish. Do NOT initiate Hinglish unless spoken to in it."}
        ]
        
        # Schedule startup greeting
        clock.Clock.schedule_once(lambda dt: self.wish_me(), 0.5)
      
        self.min_size = .2 * SCREEN_WIDTH
        self.max_size = .7 * SCREEN_WIDTH
        
        # Background
        self.add_widget(image.Image(source='static/border.eps.png', allow_stretch=True, keep_ratio=False, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        
        # Central Button (Arc Reactor)
        self.circle = JarvisButton(size_hint=(None, None), size=(284.0,284.0), background_normal='static/circle.png', pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.circle.bind(on_press=self.start_recording)
        # We manually update circle pos in update_circle, so let's keep it added but handle pos there or use pos_hint if static
        # The update_circle method updates size and pos, so we leave it, but maybe ensure it centers:
        
        # Removed self.start_recording() from here to prevent startup loop
        
        # Spinning Ring (Gif)
        self.visualizer = image.Image(source='static/jarvis.gif', size_hint=(None, None), size=(self.min_size, self.min_size))
        # Center it initially
        self.visualizer.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.add_widget(self.visualizer)
        
        # Time Display (Top Left)
        time_layout = boxlayout.BoxLayout(orientation='vertical', size_hint=(None, None), size=(200, 100), pos_hint={'x': 0.05, 'top': 0.95})
        self.time_label = label.Label(text='', font_size=24, markup=True, font_name='static/mw.ttf')
        time_layout.add_widget(self.time_label)
        self.add_widget(time_layout)
        
        clock.Clock.schedule_interval(self.update_time, 1)
        
        # Title (Top Center)
        self.title = label.Label(text='[b][color=00ffff]J.A.R.V.I.S. SYSTEM ONLINE[/color][/b]', font_size=42, markup=True, font_name='static/dusri.ttf', size_hint=(None, None), size=(600, 100), pos_hint={'center_x': 0.5, 'top': 0.95})
        self.add_widget(self.title)
        
        self.subtitles_input = textinput.TextInput(
            text='Hey Mr Stark! I am your personal assistant',
            font_size=24,
            readonly=False,
            background_color=(0, 0, 0, 0),
            foreground_color=(0, 1, 1, 1), # Cyan text
            size_hint=(0.8, None), # 80% width relative to window
            height=100,
            pos_hint={'center_x': 0.5, 'y': 0.1}, # Center horizontally, 10% from bottom
            font_name='static/teesri.otf',
        )

        self.add_widget(self.subtitles_input)
        

        self.add_widget(self.circle)
        keyboard.add_hotkey('`',self.start_recording)
        
    def take_command(self):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                r.pause_threshold = 2.0
                r.energy_threshold = 400
                r.dynamic_energy_threshold = True
                r.adjust_for_ambient_noise(source, duration=1.0)
                
                audio = r.listen(source, timeout=10, phrase_time_limit=None)
            
            try:
                print("Recognizing....")
                queri = r.recognize_google(audio, language='en-in')
                return queri.lower()

            except Exception:
                speak("Sorry I couldn't understand. Can you please repeat that?")
                queri = 'None'
                
    def start_recording(self, *args):
            if self.is_listening:
                print("Already listening...")
                return
                
            print("recording started")
            self.is_listening = True
            # Visual Feedback: Green for listening
            self.circle.background_color = (0, 1, 0, 1) 
            threading.Thread(target=self.run_speech_recognition).start()
            print("recording ended") 
            
            
    def run_speech_recognition(self):
            print('before speech rec obj')
            r = sr.Recognizer()
            r.pause_threshold = 2.0 # Increased to 2.0s to allow thinking pauses
            r.energy_threshold = 400 # Slightly higher default
            r.dynamic_energy_threshold = True
            
            with sr.Microphone() as source:
                print("Listening...")
                try:
                    r.adjust_for_ambient_noise(source, duration=1.0) # Calibrate noise
                    # phrase_time_limit=None allows indefinite listening until silence
                    audio=r.listen(source, timeout=None, phrase_time_limit=None)
                except sr.WaitTimeoutError:
                    print("Timeout listening")
                    self.is_listening = False
                    self.circle.background_color = (1, 1, 1, 1)
                    return 'None'
                
                print("audio recorded")
                
            print("after speech rec obj") 
            
            # Visual Feedback: Cyan for processing
            self.circle.background_color = (1, 1, 1, 1)

            query = 'None'
            try:
                query=r.recognize_google(audio,language="en-in") 
                print(f'Recognised: {query}')
                clock.Clock.schedule_once(lambda dt: setattr(self.subtitles_input,'text',query))
                self.handle_jarvis_commands(query.lower())
                                
            except sr.UnknownValueError:
                print("Google speech recognition could not understand audio")
                
            except sr.RequestError as e:
                print(e) 
            
            self.is_listening = False
            return query.lower()  

    def speak_and_log(self, text):
        """Speaks the text and adds it to conversation history."""
        self.conversation_history.append({"role": "assistant", "content": text})
        speak(text)  
        
    def update_time(self,dt):
            current_time = time.strftime('TIME\n\t%H:%M:%S')
            self.time_label.text = f'[b][color=00ffff]{current_time}[/color][/b]'
              
    def update_circle(self, dt):
        try:
            # Use recent history (last 10 frames) for more responsive pulsing
            recent_volume = self.volume_history[-10:] if len(self.volume_history) > 10 else self.volume_history
            self.size_value = int(np.mean(recent_volume))
            
        except Exception as e:
            self.size_value = self.min_size
            print('Warning:',e)
            
        if self.size_value <= self.min_size:
            self.size_value = self.min_size
        elif self.size_value >= self.max_size:
            self.size_value = self.max_size                                     
        self.circle.size = (self.size_value,self.size_value)
        # self.circle.pos = (...) # Removed manual pos to let pos_hint handle centering
        pass
            
            
    def update_volume(self,indata,frames,time,status):
            volume_norm = np.linalg.norm(indata) * 200
            self.volume = volume_norm
            self.volume_history.append(volume_norm)
                
            if len(self.volume_history) > self.volume_history_size:
                self.volume_history.pop(0)  
                
    def start_listening(self):
            self.stream = sd.InputStream(callback=self.update_volume) 
            self.stream.start()

    def wish_me(self):
        hour = int(time.strftime("%H"))
        if hour >= 0 and hour < 12:
            greeting = "Good Morning, Sir."
        elif hour >= 12 and hour < 18:
            greeting = "Good Afternoon, Sir."
        else:
            greeting = "Good Evening, Sir."
        
        self.speak_and_log(f"{greeting} Jarvis is online and systems are nominal.")
        self.start_recording()
        
    def check_system_stats(self):
        battery = psutil.sensors_battery()
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_total = round(ram.total / (1024**3), 2)
        
        os_info = f"{platform.system()} {platform.release()}"
        processor = platform.processor()
        
        status = f"System Report: Operating System is {os_info}. Processor is {processor}. " \
                 f"RAM is {ram_total} Gigabytes. CPU is at {cpu_usage} percent capacity."
                 
        if battery:
             status += f" Power levels at {battery.percent} percent."
             if battery.power_plugged:
                 status += " We are currently charging."
        
        self.speak_and_log(status)

    def check_internet_speed(self):
        self.speak_and_log("Running network diagnostic... this may take a moment.")
        try:
            # Patch sys.stderr for speedtest-cli compatibility with Kivy
            # Kivy replaces stderr with a Logger object that lacks fileno(), crashing speedtest on import
            original_stderr = sys.stderr
            try:
                # Fallback to original stderr if current one is broken
                if not hasattr(sys.stderr, 'fileno'):
                     if hasattr(sys, '__stderr__') and sys.__stderr__ is not None:
                         sys.stderr = sys.__stderr__
                     else:
                         # Last resort: mock it
                         class Mockfile:
                             def fileno(self): return 2
                             def write(self, x): pass
                             def flush(self): pass
                         sys.stderr = Mockfile()
                
                import speedtest
            finally:
                sys.stderr = original_stderr
                
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = float(st.download()) / 1024 / 1024
            upload_speed = float(st.upload()) / 1024 / 1024
            
            download_speed = round(download_speed, 2)
            upload_speed = round(upload_speed, 2)
            
            self.speak_and_log(f"Download speed is {download_speed} Megabits per second. " \
                               f"Upload speed is {upload_speed} Megabits per second.")
            print(f"Download: {download_speed} Mbps, Upload: {upload_speed} Mbps")
        except Exception as e:
            self.speak_and_log("I could not perform the speed test due to a network error.")
            print(f"Speedtest error: {e}")
    
    def get_groq_response(self, query):
        try:
            # Add user query to memory
            self.conversation_history.append({"role": "user", "content": query})
            
            chat_completion = groq_client.chat.completions.create(
                messages=self.conversation_history,
                model="llama-3.3-70b-versatile", 
            )
            
            response = chat_completion.choices[0].message.content
            
            # Add AI response to memory
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            print(f"Error getting Groq response: {e}")
            return "My apologies, Sir. I seem to be having trouble connecting to the network."
            
    def handle_jarvis_commands(self,query):  
            try:
                if "how are you" in query or "system status" in query or "status report" in query or "health" in query or "battery" in query or "cpu" in query or "specs" in query or "machine info" in query:
                    self.check_system_stats()

                # --- Universal App Control (High Priority) ---
                # --- Universal App Control (High Priority) ---
                elif "stop" in query or "pause" in query:
                     self.speak_and_log("Pausing media.")
                     pyautogui.press('playpause')

                elif "close" in query and "tab" in query:
                    self.speak_and_log("Closing tab.")
                    pyautogui.hotkey('ctrl', 'w')
                    
                elif "close" in query:
                    app_name = query.replace("close ", "").strip()
                    self.speak_and_log(f"Closing {app_name}")
                    app_close(app_name, match_closest=True, output=False)
                    

                     
                elif "type" in query and "error by night" not in query: # Exclude the subscribe script specific typing
                    text = query.replace("type ", "")
                    pyautogui.write(text, interval=0.05)
                
                elif "press" in query: 
                    key = query.replace("press ", "").strip()
                    pyautogui.press(key)
                    
                elif "click" in query and "subscribe" not in query:
                    pyautogui.click()
                
                # --- End Universal Control ---

 

                elif "internet speed" in query or "network speed" in query or "check speed" in query:
                    threading.Thread(target=self.check_internet_speed).start() # Threading to prevent freezing UI

                elif "open command prompt" in query:
                    speak("Opening command prompt")
                    os.system('start cmd')

                elif "open camera" in query:
                    speak("Opening camera sir")
                    sp.run('start microsoft.windows.camera:', shell=True)

                elif "open notepad" in query:
                    speak("Opening Notepad for you sir")
                    os.system('notepad.exe')

                elif "open discord" in query:
                    speak("Opening Discord for you sir")
                    # Try default location or just launch if in path
                    discord_path = os.environ.get("DISCORD_PATH")
                    if discord_path and os.path.exists(discord_path):
                         os.startfile(discord_path)
                    else:
                        # Fallback to trying to run blindly
                        try:
                            os.startfile("Discord.exe")
                        except Exception:
                            speak("I could not find Discord path. Please set it in environment variables.")

                elif "open gta" in query:
                    speak("Opening Gta for you sir")
                    gta_path = os.environ.get("GTA_PATH")
                    if gta_path and os.path.exists(gta_path):
                        os.startfile(gta_path)
                    else:
                        speak("GTA path is not configured.")


                elif 'ip address' in query:
                    ip_address = find_my_ip()
                    speak(
                        f'Your IP Address is {ip_address}.\n For your convenience, I am printing it on the screen sir.')
                    print(f'Your IP Address is {ip_address}')

                elif "play" in query and "close" not in query and "stop" not in query and "pause" not in query:
                    # Smart extraction: remove 'play', 'on youtube', 'song'
                    song_name = query.replace("play", "").replace("on youtube", "").replace("youtube", "").replace("song", "").strip()
                    
                    if song_name:
                         self.speak_and_log(f"Playing {song_name} on YouTube.")
                         youtube(song_name)
                    else:
                         self.speak_and_log("What do you want to play on youtube sir?")
                         video = self.take_command().lower()
                         youtube(video)

                elif "search on google" in query:
                    speak(f"What do you want to search on google")
                    query = self.take_command().lower()
                    search_on_google(query)

                elif "search on wikipedia" in query:
                    speak("what do you want to search on wikipedia sir?")
                    self.speak_and_log("what do you want to search on wikipedia sir?")
                    search = self.take_command().lower()
                    results = search_on_wikipedia(search)
                    self.speak_and_log(f"According to wikipedia,{results}")
                

                elif "send" in query and "email" in query:
                    self.speak_and_log("Who is the recipient? Please enter email address in console.")
                    receiver_add = input("Email address: ")
                    self.speak_and_log("What is the subject, sir?")
                    subject = self.take_command().lower()
                    self.speak_and_log("What is the message?")
                    message = self.take_command().lower()
                    if send_email(receiver_add, subject, message):
                        self.speak_and_log("I've sent the email sir.")
                    else:
                        self.speak_and_log("Something went wrong while sending email.")

                elif "weather" in query:
                    # Attempt to extract city from the query first
                    # e.g. "tell me weather in mumbai" -> "tell me weather in" removed -> "mumbai"
                    formatted = query.replace("weather", "").replace("in", "").replace("tell", "").replace("me", "").replace("about", "").replace("what", "").replace("is", "").replace("the", "").replace("check", "").strip()
                    
                    if formatted and len(formatted) > 2:
                        city = formatted
                        self.speak_and_log(f"Checking weather for {city}...")
                    else:
                        self.speak_and_log("Which city sir?")
                        city = self.take_command().lower()
                        
                    if city and city != 'none':
                        try:
                            weather, temp, feels_like = weather_forecast(city)
                            self.speak_and_log(f"The current temperature is {temp}, but it feels like {feels_like}")
                            self.speak_and_log(f"Also, the weather report talks about {weather}")
                        except Exception:
                            self.speak_and_log(f"I couldn't find weather data for {city}")
                    else:
                        self.speak_and_log("I didn't catch the city name, Sir.")

                elif "news" in query:
                    self.speak_and_log("Here are the latest news headlines.")
                    headlines = get_news()
                    for headline in headlines:
                        self.speak_and_log(headline)

                elif "movie" in query:
                    movies_db = imdb.IMDb()
                    self.speak_and_log("Please tell me the movie name:")
                    text = self.take_command()
                    movies = movies_db.search_movie(text)
                    self.speak_and_log("searching for " + text)
                    if not movies:
                         self.speak_and_log("No movies found.")
                    else:
                        self.speak_and_log("I found these")
                        for movie in movies[:2]: # Limit to 2 to avoid long speaking
                            title = movie["title"]
                            year = movie.get("year", "Unknown Year")
                            self.speak_and_log(f"{title}-{year}")
                            # Detailed info might fail if movieID not fetched, keep simple for now or try/except
                            try:
                                info = movie.movieID
                                movie_info = movies_db.get_movie(info)
                                rating = movie_info.get("rating", "N/A")
                                plot = movie_info.get('plot outline', 'plot summary not available')
                                self.speak_and_log(f"{title} was released in {year}, rating {rating}. {plot[:100]}...")
                            except:
                                pass


                elif 'subscribe' in query:
                    speak(
                        "Everyone who are watching this video, Please subscribe for more amazing content from error by "
                        "night. I will show you how to do this")
                    speak("Firstly Go to youtube")
                    webbrowser.open("https://www.youtube.com/")
                    speak("click on the search bar")
                    pyautogui.moveTo(806, 125, 1)
                    pyautogui.click(x=806, y=125, clicks=1, interval=0, button='left')
                    speak("Error by night")
                    pyautogui.typewrite("Error by night", 0.1)
                    time.sleep(1)
                    speak("press enter")
                    pyautogui.press('enter')
                    pyautogui.moveTo(971, 314, 1)
                    speak("Here you will see our channel")
                    pyautogui.moveTo(1688, 314, 1)
                    speak("click here to subscribe our channel")
                    pyautogui.click(x=1688, y=314, clicks=1, interval=0, button='left')
                    speak("And also Don't forget to press the bell icon")
                    pyautogui.moveTo(1750, 314, 1)
                    pyautogui.click(x=1750, y=314, clicks=1, interval=0, button='left')
                    speak("turn on all notifications")
                    pyautogui.click(x=1750, y=320, clicks=1, interval=0, button='left')
            
                # Legacy Open commands (can be replaced by AppOpener eventually, but keeping for reliability)
                elif "open" in query: 
                    # e.g. "open spotify" -> "spotify"
                    # But we must avoid re-triggering if it was "open command prompt" handled above?
                    # Wait, the `elif` chain prevents re-entry.
                    # So if I move "Open Command Prompt" etc. to be `elif` strictly, it works.
                    # Currently "Open Command Prompt" IS an `elif`.
                    
                    app_name = query.replace("open ", "").strip()
                    self.speak_and_log(f"Attempting to open {app_name}")
                    app_open(app_name, match_closest=True, output=False)
            
                else:
                    groq_response = self.get_groq_response(query)
                    groq_response = groq_response.replace("*","")
                    if groq_response and groq_response != "I'm sorry, I couldn't process that request.":
                        speak(groq_response)
                        print(groq_response)
                
            except Exception as e:
                print(e)