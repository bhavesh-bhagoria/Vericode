import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://ws-03yf1xwqq43yfujk.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
    timeout=30.0,
)

print("Before request")

response = client.chat.completions.create(
    model="kimi-k3",
    messages=[
        {
            "role": "user",
            "content": "Say hello in one word."
        }
    ]
)

print("After request")
print(response.choices[0].message.content)
