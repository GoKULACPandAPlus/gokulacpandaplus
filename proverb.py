import os
from dotenv import load_dotenv
import chatgpt

load_dotenv(".env")
chatbot = chatgpt.ChatBot(api_key = os.environ.get("OPENAI_API_KEY"))
prompt = "偉人の英語の格言を１つ選び「（英語の格言）（格言の和訳）（作者）」の形式で教えてください"
message = chatbot.chat(prompt)
print(message)