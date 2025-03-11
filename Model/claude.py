import anthropic


def connect_api(key=r''):
    if not key:
        key = input("Enter API Key - ").strip()
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=key,
    )
    return client


def chat_claide(client, model_name='claude-3-haiku-20240307', test=False):
    print()
    if test:
        prompt = "Hello, Claude - You are a world-class poet. Respond only with short poems. A poem on oceans."
        print("User> ", prompt)
    else:
        prompt = input("User> ")
    message = client.messages.create(
        model=model_name,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print("\nAgent> ", end="")
    print(message.content[0].text)


if __name__ == "__main__":
    chat_claide(connect_api(), test=False)