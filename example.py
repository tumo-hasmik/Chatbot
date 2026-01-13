from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

user_prompt = input("Enter your prompt!!")

input_messages = [
    {"role": "system", "content": 
    "You are a helpful assistant that answers clearly."
    "You are specialized in music and you can answer to every question about music."
    "Avoid unnecessary jargon. "
    "The users can sing songs, write lyrics, etc and you will be able to play the continuing of the song."
    },
    {"role": "user", "content": "Explain recursion in simple terms."}
]

response = client.responses.create(
    model = "gpt-5-nano",
    input = user_prompt
)

print(response.output_text)