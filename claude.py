import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")  # Safely pulls from env
)

message = client.messages.create(
    model="claude-3-5-haiku-20241022",  # current stable version
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)

print(message.content)
