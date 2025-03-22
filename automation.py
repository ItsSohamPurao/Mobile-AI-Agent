# Import required libraries
from AppOpener import close, open as appopen # Import functions to open and close apps.
from webbrowser import open as webopen # Import web browser functionality.
from pywhatkit import search, playonyt # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup # Import BeautifulSoup for parsing HTML content.
from rich import print # Import rich for styled console output.
from groq import Groq # Import Groq for Al chat functionalities.
import webbrowser # Import webbrowser for opening URLS.
import subprocess # Import subprocess for interacting with the system.
import requests # Import requests for making HTTP requests.
import keyboard # Import keyboard for keyboard-related actions.
import asyncio # Import asyncio for asynchronous programming.
import os # Import os for operating system functionalities.
# Load environment variables from the .env file.
env_vars=dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey") # Retrieve the Grog API key,
# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgkElc", "LTK00 SY7ric", "ZOLCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
"tw-Data-text tw-text-small tw-ta",
"IZ6rdc", "05uR6d LTK00", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
"dDoNo ikb4Bb gsrt", "sXLa0e",
"LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]
# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

#Fredefined professional responses for user interactions.
professional_responses = [
"Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
"I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]
#List to store chatbot messages.
messages = []
#System Dessage to provide context to the chatoot.
SystemChatBot = [{"role": "system", "content": "Hello, I am (os.environ['username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]
#Function to perform a Google search.
# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic) # Use pywhatkit's search function to perform a Google search.
    return True # Indicate success.
# Function to generate content using AI and save it to a file.
def Content (Topic):
# Nested function to open a file in Notepad.
    def OpenNotepad (File):
        default_text_editor = 'notepad.exe' # Default text editor.
        subprocess.Popen([default_text_editor, File]) # Open the file in Notepad.
        # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f" [prompt]"}) # Add the user's prompt to messages.
        
        completion = client.chat.completions.create(
        model="mixtral-8x7b-32768", # Specify the AI model.
        messages= SystemChatBot + messages, # Include system instructions and chat history.
        max_tokens=2048, # Limit the maximum tokens in the response.
        temperature=0.7, # Adjust response randomness.
        top_p=1, # Use nucleus sampling for response diversity.
        stream=True, # Enable streaming response.
        stop=None # Allow the model to determine stopping conditions.
        )
        Answer = ""# Initialize an empty string for the response.

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" # Construct the YouTube search URL.
    webbrowser.open(Url4Search) # Open the search URL in a web browser.
    return True # Indicate success.
# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query) # Use pywhatkit's playonyt function to play the video.
    return True # Indicate success.
# Function to open an application or a relevant webpage.
# Function to open an application or a relevant webpage.
def OpenApp(app,sess=requests.session()):
    try:
        appopen(app, match_closest =True, output=True, throw_error=True) # Attempt to open the app.
        return True # Indicate success.
    except:
    # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser') # Parse the HTML content.
            links = soup.find_all('a', {'jsname': 'UWckNb' }) # Find relevant links.
            return [link.get('href') for link in links] # Return the links.
        # Nested function to perform a Google search and retrieve HTML.
        
        def search_google(query):
            url =f"https://www.google.com/search?q={query}" # Construct the Google search URL.
            headers = {"User-Agent": useragent} # Use the predefined user-agent.
            response = sess.get(url, headers-headers) # Perform the GET request.
            if response.status_code == 200:
                return response.text # Return the HTML content.
            else:
                print("Failed to retrieve search results.") # Print an error message.
            return None
        
        html = search_google(app) 
        # Perform the Google search.
        if html:
            link =  extract_links(html)[0] # Extract the first link from the search results.
        webopen(link) # Open the link in a web browser.
    return True # Indicate success.

# Function to close an application.
def CloseApp(app):
    if "chrome" in app:
        pass # Skip if the app is Chrome.
    else:
        try:
            close(app, match_closest =  True, output=True, throw_error=True) # Attempt to close the app.
            return True # Indicate success.
        except:
            return False # Indicate failure.
        
# Function to execute system-level commands.
def System(command):
# Nested function to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute") # Simulate the mute key press.
    # Nested function to unmute the system volume.
    def unmute():
        keyboard.press_and_release("volume mute") # Simulate the unmute key press.
    # Nested function to increase the system volume.
    def volume_up():
        keyboard.press_and_release("volume up") # Simulate the volume up key
    # Nested function to decrease the system volume.
    def volume_down():
        keyboard.press_and_release("volume down") # Simulate the volume down key press.
    # Execute the appropriate command.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True # Indicate success. I

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list [str]):
    funcs = [] # List to store asynchronous tasks.
    for command in commands:
        if command.startswith("open "): # Handle "open" commands.
            if "open it" in command: # Ignore "open it" commands.
                pass
            if "open file" == command: # Ignore "open file" commands.
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command. removeprefix( "open "))# Schedule app opening.
                funcs.append(fun)
        elif command. startswith("general "):# Placeholder for general commands.
            pass
        elif command. startswith( "realtime") :# Placeholder for real-time commands.
            pass
        elif command. startswith( "close "):# Handle "close" commands.
            fun = asyncio. to_thread(CloseApp, command. removeprefix( "close "))# Schedule app closing.
            funcs.append(fun)
        elif command. startswith("play "): # Handle "play" commands.
            fun = asyncio. to_thread(PlayYoutube, command. removeprefix( "play "))# Schedule YouTube playback.
        elif command. startswith("content "): # Handle "content" commands.
            fun = asyncio. to_thread(Content, command. removeprefix("content "))# Schedule content creation.
            funcs . append( fun)
        elif command.startswith("google search "):# Handle Google search commands
            fun = asyncio. to_thread(GoogleSearch, command. removeprefix( "google search"))# Schedule Google search.
            funcs . append( fun)
        elif command. startswith( "youtube search "): # Handle YouTube search commands
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search# Schedule YouTube search."))