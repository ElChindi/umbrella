import pyjokes
import speech_recognition as sr
from GoogleNews import GoogleNews
from datetime import date
from datetime import datetime
import difflib
from gtts import gTTS
from playsound import playsound
import os


# STT CODE

def speechToText(silencedOutput = False, waitingLimit = True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            if not silencedOutput: print(" > Listening...")
            if waitingLimit:
                audio = r.listen(source, phrase_time_limit=10, timeout=5)
            else:
                audio = r.listen(source, phrase_time_limit=10)

        except:
            global idle 
            idle = True
            return []
        try:
            text = r.recognize_google(audio).lower().split()
            if any(elem in ["cancel", "stop", "break"]  for elem in text):
                print("stop")
                global stopAction
                stopAction = True
                return []

        except sr.UnknownValueError:
            return []

        except sr.RequestError:
            textToSpeech("Sorry, there was a problem with google")
            return []
        return text


def sleeping():
    print(" > Sleeping...")
    text = []

    while 'umbrella' not in text:
        try:
            text = speechToText(silencedOutput=True, waitingLimit=False)
        except sr.UnknownValueError:
            text = []
        except sr.RequestError:
            text = []


# TTS CODE

def textToSpeech(answerText, language='en'):
    print(answerText)
    tts = gTTS(text=answerText,lang=language,slow=False)
    if os.path.exists('speech.mp3'):
        os.remove('speech.mp3')
    tts.save('speech.mp3')
    playsound('speech.mp3')



# ACTIONS

# Get information of the input in a list of words
def actions(words):

    # Fill in emergency agenda in a dictionary
    e_dictionary = open('emergency_agenda.txt', 'r', encoding='utf-8')
    emergency_agenda = {}
    for line in e_dictionary:
        key, value = line.split("\t")
        emergency_agenda[key] = value.rstrip("\n")


    # Fill in agenda in a dictionary
    dictionary = open('agenda.txt', 'r', encoding='utf-8')
    agenda = {}
    for line in dictionary:
        key, value = line.split("\t")
        agenda[key] = value.rstrip("\n")

    # ACTIONS TO CHOOSE ------------------------------------------------------------------------------------------------------------------------
    # Check what action to do depending on the words of the list
    
    # EMERGENCY
    if any(emergency in emergency_agenda  for emergency in words):
        return emergency(words, emergency_agenda)
            
    # CALL
    elif any(elem in ["call", "calling", "phone", "telephone"]  for elem in words):
        return call(words, agenda)
    
    # DATE
    elif any(elem in ["date", "day"]  for elem in words):
        return get_date()
    
    # TIME
    elif any(elem in ["time", "clock", "hour"]  for elem in words):
        return time()
    
    # WEATHER
    elif any(elem in ["weather", "forecast"]  for elem in words):
        return weather()
        
    # NEWS
    elif any(elem in ["news", "newspaper"]  for elem in words):
        return news()

    # JOKE
    elif any(elem in ["jokes", "joke", "gag"]  for elem in words):
        return joke()

    # EXIT
    elif any(elem in ["exit", "close", "goodbye"]  for elem in words):
        textToSpeech("Closing umbrella")
        exit()

    # If not option found ask for repetition to the user
    else:
        return ""





# ACTIONS ----------------------------------------------------------------------------------------------------------------------------
# Actions called from previous section

# WHICH IS THE PHONE NUMBER FOR SOME EMERGENCY?
def emergency(words, emergency_agenda):

    for emergency in emergency_agenda:
        if emergency in words:
            number = ""
            #Search phone number in agenda
            for e in emergency_agenda[emergency]:
                number = number + e + " "
            
            return f"The phone number for {emergency} is the {number}"

    return "No phone number registered"

# WHICH IS THE PHONE NUMBER OF SOMEONE?
def call(words, agenda):
    nameDetected = False
    name = []
    for word in words:
        name = difflib.get_close_matches(word, agenda.keys())
        if name:
            nameDetected = True #it has name
    
    #Without name --> Ask name to user first
    if not nameDetected:
        #tts
        textToSpeech("Who do you want to call?")
        #stt
        words = speechToText()
        if stopAction:
            return "Action cancelled!"

    #With name
    for word in words:
        if not nameDetected: #already done
            name = difflib.get_close_matches(word, agenda.keys())

        #print(word, name)
        number = ""
        if name:
            #Search phone number in agenda
            for e in agenda[name[0]]:
                number = number + e + " "
            return f"The phone number of {name[0]} is {number}"

    return "No phone number registered"
    
# WHAT DATE IS TODAY?
def get_date():
    return date.today().strftime("%B %d, %Y")


# WHAT TIME IS IT?
def time():
    # SOURCE: https://www.geeksforgeeks.org/convert-given-time-words/
    currTime = datetime.now()
    h = currTime.hour
    m = currTime.minute
    nums = ["zero", "one", "two", "three", "four",
            "five", "six", "seven", "eight", "nine",
            "ten", "eleven", "twelve", "thirteen",
            "fourteen", "fifteen", "sixteen",
            "seventeen", "eighteen", "nineteen",
            "twenty", "twenty one", "twenty two",
            "twenty three", "twenty four",
            "twenty five", "twenty six", "twenty seven",
            "twenty eight", "twenty nine"]
 
    if (m == 0):
        return f"{nums[h]} o' clock"
 
    elif (m == 1):
        return f"one minute past {nums[h]}"
 
    elif (m == 59):
        return f"one minute to {nums[(h % 12) + 1]}"
 
    elif (m == 15):
        return f"quarter past {nums[h]}"
 
    elif (m == 30):
        return f"half past {nums[h]}"
 
    elif (m == 45):
        return f"quarter to {nums[(h % 12) + 1]}"
 
    elif (m <= 30):
        return f"{nums[m]} minutes past {nums[h]}"
 
    elif (m > 30):
        return f"{nums[60 - m]} minutes to {nums[(h % 12) + 1]}"


# WHAT CURRENT WEATHER IS THERE IN A CITY?
def weather():
    # SOURCE: https://www.geeksforgeeks.org/python-find-current-weather-of-any-city-using-openweathermap-api/

    # IMPORTS
    import requests, json

    # Enter your API key here
    api_key = "c7b2ae00d95d037044e7d99f63df6599"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Give city name
    textToSpeech("Please, say a location")
    city_name = ' '.join(speechToText())
    
    if stopAction:
            return "Action cancelled!"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    # Check the value of "cod" key is equal to "404" means city is found, otherwise city is not found
    if x["cod"] != "404":

        y = x["main"]

        # store value of temperature
        current_temperature = y["temp"]

        # store value of pressure
        current_pressure = y["pressure"]

        # store value of humidity
        current_humidiy = y["humidity"]

        # store the value of "weather"
        z = x["weather"]

        # store a brief "description" of the weather
        weather_description = z[0]["description"]

        # print following values
        '''
        print(" Temperature (in celsius unit) = " +
                        str(round(float(current_temperature) - 273.15)) + 
                "\n atmospheric pressure (in hPa unit) = " +
                        str(current_pressure) +
                "\n humidity (in percentage) = " +
                        str(current_humidiy) +
                "\n description = " +
                        str(weather_description))
        '''

        return  f"{city_name} has {str(weather_description)}, with a temperature of {str(round(float(current_temperature) - 273.15))} celsius degrees, an atmospheric pressure of {str(current_pressure)} hectopascals and a humidity of {str(current_humidiy)} %"
    else:
        return "City not found"


def news():
    try:
        textToSpeech("Please, say a topic or location to search the latest news")
        searchWord = ' '.join(speechToText())

        if stopAction:
            return "Action cancelled!"

        textToSpeech("Searching news, please wait a moment")
        if searchWord:
            googlenews = GoogleNews(lang='en', period='1d', encode='utf-8')
            googlenews.get_news(searchWord)
            googlenews.search(searchWord)
            googlenews.get_page(2)
            
            allNews = googlenews.get_texts()
            newsList = []
            count = 0

            for news in allNews:
                # Check for complete news to return
                if "..." not in news and count<5:
                    count+=1
                    newsList.append(news)
            googlenews.clear()

            if newsList:
                return '\n'.join(newsList)

            return "No news found!"
    except:
        return "Sorry, news are not yet available!"


def joke():
    try:
        return pyjokes.get_joke(category = 'all', language='en')
    except:
        print("Sorry, we cannot offer jokes right now!")



# MAIN CODE


print("""\
           
                                         ██
                                   ██████████████
                             ██████░░██░░██░░██░░██████
                         ████░░░░░░██░░░░░░██░░██░░░░░░████
                       ██░░░░░░░░██░░░░░░░░██░░░░██░░░░░░░░██
                     ██░░░░░░░░██░░░░░░░░░░░░██░░░░██░░░░░░░░██
                   ██░░░░░░░░░░██░░░░░░░░░░░░██░░░░░░██░░░░░░░░██
                 ██░░░░░░░░░░░░██░░░░░░░░░░░░██░░░░░░░░██░░░░░░░░██
                 ██░░░░░░░░░░▓▓▒▒░░░░░░░░░░░░██░░░░░░░░▒▒▓▓░░░░░░██
               ██░░░░██████░░██░░██████████░░██░░██████░░██░░██░░░░██
               ██░░██▒▒▒▒▒▒██████▒▒▒▒▒▒██░░██████▒▒▒▒▒▒██████▒▒██░░██
               ████▒▒▒▒▒▒▒▒▒▒░░▒▒▒▒▒▒▒▒██░░██░░▒▒▒▒▒▒▒▒▒▒░░▒▒▒▒▒▒████
               ░░████████▒▒▒▒▒▒████▒▒▒▒██░░██▒▒▒▒▒▒████▒▒▒▒██████  ░░
                         ██░░██    ██░░██░░████░░██    ██░░
                                       ██░░██
         ▄▄   ▄▄ ▄▄   ▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   ▄▄▄▄▄▄▄ ▄▄▄     ▄▄▄     ▄▄▄▄▄▄ 
         █  █ █  █  █▄█  █  ▄    █   ▄  █ █       █   █   █   █   █      █
         █  █ █  █       █ █▄█   █  █ █ █ █    ▄▄▄█   █   █   █   █  ▄   █
         █  █▄█  █       █       █   █▄▄█▄█   █▄▄▄█   █   █   █   █ █▄█  █
         █       █       █  ▄   ██    ▄▄  █    ▄▄▄█   █▄▄▄█   █▄▄▄█      █
         █       █ ██▄██ █ █▄█   █   █  █ █   █▄▄▄█       █       █  ▄   █
         █▄▄▄▄▄▄▄█▄█   █▄█▄▄▄▄▄▄▄█▄▄▄█  █▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█▄█ █▄▄█
           
                                       ██░░██
                                       ██░░██
                                 ████  ██░░██
                                 ██░░██░░░░██   
                                 ██░░░░░░██
                                   ██████
                                   
                        """)


print("WELCOME TO UMBRELLA!")
print("")
print('''First you have to open Umbrella saying "Umbrella". Then choose an action of the following (you can do this by pronouncing the uppercase words):
    - Get an EMERCENGY phone number
    - Get phone number of agenda to CALL
    - Get today's DATE
    - Get the current TIME
    - Get the current WEATHER
    - Get the latest NEWS
    - Get some JOKE
    - EXIT Umbrella''')
print("")

while True:
    sleeping()
    textToSpeech("How can I help you?")
    count = 0
    responce = ""
    while count < 3 and not responce:
        stopAction = False
        idle = False
        text = speechToText()
        if idle: break
        responce = actions(text)
        if count == 2 and not responce:
            textToSpeech("Sorry, I don't know what to do")
            break
        if responce:
            textToSpeech(responce)
        else:
            textToSpeech("Sorry, could you please repeat that?")
        count += 1
