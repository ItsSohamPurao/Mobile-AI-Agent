import cohere # Import the Cohere Library for AI services.
from rich import print #Import the Rich library to enhance terminal outputs,
from dotenv import dotenv_values # Import dateny to load environment variables from a .env file.
# Load environment variables from the .env file.
env_vars=dotenv_values(".env")

#Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API key.
co= cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs= [
"exit", "general", "realtime", "open", "close", "play",
"system", "content", "google search",
"youtube search", "reminder"
]
# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook', 'close notepad', etc.
*** Do not answer any query, just decide what kind of query is given to you. ***

→ Respond with 'general (query)' if a query can be answered by an LLM model (conversational AI chatbot) and doesn't require any real-time information. For example, if the query is 'who was Akbar?', respond with 'general who was Akbar?'. If the query is 'how can I study more effectively?', respond with 'general how can I study more effectively?'.

→ Respond with 'realtime (query)' if a query cannot be answered by an LLM model (because they don't have real-time data) and requires up-to-date information. For example, if the query is 'what is the current weather in New York?', respond with 'realtime what is the current weather in New York?'.

→ Respond with 'open (application name or website name)' if a query is asking to open any application or website. For example, if the query is 'open facebook', respond with 'open facebook'. If the query is 'open chrome', respond with 'open chrome'.

→ Respond with 'close (application name)' if a query is asking to close any application. For example, if the query is 'close notepad', respond with 'close notepad'. If the query is 'close facebook', respond with 'close facebook'.

→ Respond with 'play (song name)' if a query is asking to play any song. For example, if the query is 'play afsanay by ys', respond with 'play afsanay by ys'. If the query is 'play let her go', respond with 'play let her go'.

→ Respond with 'generate image (image prompt)' if a query is requesting to generate an image with a given prompt. For example, if the query is 'generate image of a sunset over the mountains', respond with 'generate image of a sunset over the mountains'.

→ Respond with 'system (task name)' if a query is asking to perform a system-related task like mute, unmute, volume up, volume down, etc. For example, if the query is 'mute the volume', respond with 'system mute the volume'. If the query is 'increase the brightness', respond with 'system increase the brightness'.

→ Respond with 'content (topic)' if a query is asking to write any type of content like an application, code, email, or anything else. For example, if the query is 'write an email to my manager', respond with 'content write an email to my manager'. If the query is 'write a Python script to calculate the sum of two numbers', respond with 'content write a Python script to calculate the sum of two numbers'.

→ Respond with 'google search (topic)' if a query is asking to search for a specific topic on Google. For example, if the query is 'search for the latest news on AI', respond with 'google search latest news on AI'. If the query is 'search for Python tutorials', respond with 'google search Python tutorials'.

→ Respond with 'youtube search (topic)' if a query is asking to search for a specific topic on YouTube. For example, if the query is 'search for machine learning tutorials on YouTube', respond with 'youtube search machine learning tutorials'. If the query is 'search for music videos on YouTube', respond with 'youtube search music videos'.

*** If the query is asking to perform multiple tasks like 'open facebook, telegram, and close whatsapp', respond with 'open facebook, open telegram, close whatsapp'. ***

*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis', respond with 'exit'. ***

*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not recognized. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]
# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})
    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model='command-r-plus',  # Specify the Cohere model to use.
        message=prompt,  # Pass the user's query.
        temperature=0.7,  # Set the creativity level of the model.
        chat_history=ChatHistory,  # Provide the predefined chat history for context.
        prompt_truncation='OFF',  # Ensure the prompt is not truncated.
        connectors=[],  # No additional connectors are used.
        preamble=preamble  # Pass the detailed instruction preamble.
    )

    # Initialize an empty string to store the generated response.
    response = ""
    # Iterate over events in the stream and capture text generation events.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text  # Append generated text to the response.
    # Remove newline Characters T and split responses into individual tasks.
    response = response.replace("\n", "")
    response = response.split(",")
    # Strip leading and trailing whitespaces from each task.
    response = [i.strip() for i in response]
    # Initialize an empty list to filter valid tasks.
    temp = []
    # Filter the tasks based on recognized function keywords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)  # Add valid tasks to the filtered list.
    # Update the response with the filtered list of tasks.
    response = temp
    # If '(query)' is in the response, recursively call the function for further clarification.
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse  # Return the clarified response.
    
    # Fallback if no valid tasks are found
    if not response:
        response = ["general (query)"]
    
    # Return the final response
    return response

# Entry point for the script.
if __name__ == "__main__":
# Continuously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>> "))) # Print the categorized response