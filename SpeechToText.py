from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage")
# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''
# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
with open(r"./Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get the current working directory.
current_dir = os.getcwd()

# Generate the file path for the HTML file.
Link = os.path.join(current_dir, "Voice.html")

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = os.path.join(current_dir, "Frontend", "Files")

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()  # Convert to lowercase and remove leading/trailing spaces
    query_words = new_query.split()  # Split the query into words
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom", 
        "can you", "what's", "is", "are", "do", "does", "did", "could", "would", 
        "should", "will", "shall", "has", "have", "had", "am", "is", "are", "was", 
        "were", "may", "might", "must", "ought", "need", "dare", "won't", "can't", 
        "couldn't", "wouldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't", 
        "hasn't", "haven't", "hadn't", "doesn't", "don't", "didn't"
    ]
    
    # Check if the query is a question and add a question mark if necessary
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:  # Check if the last character is already punctuation
            new_query = new_query[:-1] + "?"  # Replace the last character with a question mark
        else:
            new_query += "?"  # Add a question mark if no punctuation exists
    else:
        # Add a period if the query is not a question
        if query_words[-1][-1] in ['.', '?', '!']:  # Check if the last character is already punctuation
            new_query = new_query[:-1] + "."  # Replace the last character with a period
        else:
            new_query += "."  # Add a period if no punctuation exists
    
    return new_query.capitalize()  # Capitalize the first letter of the query

# Function to translate text to English.
def UniversalTranslator(Text):
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return Text  # Return the original text if translation fails

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get("file://" + Link)
    
    # Start speech recognition by clicking the start button.
    driver.find_element(By.ID, "start").click()
    
    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(By.ID, "output").text
            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(By.ID, "end").click()
                
                # If the input language is English, return the modified query.
                if InputLanguage.lower() == "en" or InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            print(f"Error: {e}")
            continue

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)