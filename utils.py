# utils.py

def generate_session_title(messages, client):
    prompt = (
        "Based on the following messages, generate a concise title (1-4 words) "
        "for this chat session:\n\n"
    )
    for message in messages:
        prompt += f"User: {message['message']}\n"
        prompt += f"Assistant: {message['response']}\n"

    completion = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": prompt
        }],
        model="mixtral-8x7b-32768"
    )

    return completion.choices[0].message.content.strip()
