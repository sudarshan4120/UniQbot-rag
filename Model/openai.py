import requests
import os

# Get OpenAI API key from environment variables
# openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_api_key = r""

if openai_api_key is None:
    raise ValueError("OpenAI API key is not set in environment variables.")

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

# Initialize messages list with system message
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]

# Start the chat loop
message = input("User> ")
while message and message.lower() not in ['exit', 'bye']:

    if message:
        # Add user message to the conversation history
        messages.append(
            {"role": "user", "content": message}
        )

        # Prepare the data for the API request
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }

        # Make the API request
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            print(f"ChatGPT: {reply}")

            # Add assistant's response to the conversation history
            messages.append({"role": "assistant", "content": reply})
        else:
            print(f"Error: {response.status_code} {response.text}")

    message = input("User> ")