#THIS IS THE NEW VERSION THAT TURNS spotify.py INTO A SMALL FLASK API
#HUYS UNEM ARDEN PATRASTA HORS AREV


from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
from supabase import create_client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

os.getenv("SPOTIFY_CLIENT_ID")
os.getenv("SPOTIFY_CLIENT_SECRET")

client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))

load_dotenv()
app = Flask(__name__, static_folder="static", static_url_path="")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

results = sp.artist("spotify:artist:1dfeR4HaWDbWqFHLkxsg1d")  # Queen
print(results['name'], results['genres'])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

data = supabase.table("documents").select("*").execute()
documents = data.data

print(documents)

sheet_content = "\n".join([
    f"{doc.get('topic', doc.get('title', 'No Title'))}: {doc.get('content', 'No Content')}"
    for doc in documents
])

rag_message = {
    "role": "system",
    "content": (
        "Use the retrieved context below to answer. If it doesn't contain the answer, say so. \n\n"
        f"RETRIEVED CONTEXT:\n{context if context else '(no matches)'}"
    ) }

full_user_message = {
        "role": "user",
        "content": user_message
    }

full_message = [rag_message, full_user_message, system_prompt]

resp = client.responses.create(
        model = "gpt-5-nano",
        input=full_message
    )

# sheet_content = ""
# for doc in documents:
#     topic = doc.get('topic') or doc.get('title') or "No Title"
#     content = doc.get('content') or "No Content"
#     sheet_content += f"{topic}: {content}\n"


system_prompt = [
    {"role": "system",
     "content": f"You are a music-specialized chatbot. Use this knowledge:\n{sheet_content}"}
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/spotify", methods=["POST"])
def spotify_info():
    query = request.json.get("artist")  # or song/album
    results = sp.search(query, type="artist")  # or type="track"
    return jsonify(results)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    user_input = request.json.get("prompt")
    user_prompt = {"role": "user", "content": user_input}
    messages = system_prompt + [user_prompt]

    response = client.responses.create(model="gpt-5-nano", input=messages)
    return jsonify({"response": response.output_text})

@app.get("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True, port=5001)


# THIS IS THE OLD VERSION WITHOUT FLASK
# 
# 
# 
# from dotenv import load_dotenv
# from openai import OpenAI
# from supabase import create_client
# import os

# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# data = supabase.table("documents").select("*").execute()
# documents = data.data  


# sheet_content = "\n".join([f"{doc['topic']}: {doc['content']}" for doc in documents])

# system_prompt = [
#     {
#         "role": "system",
#         "content": (
#             "You are a music-specialized chatbot.\n"
#             "You combine structured music data (artists, genres, albums, songs) with conceptual knowledge about music theory, history, and songwriting.\n"
#             "Use the following knowledge as your reference:\n"
#             f"{sheet_content}\n"
#             "When factual information about artists or songs is required, use provided data.\n"
#             "When explaining concepts, give clear and beginner-friendly explanations.\n"
#             "If the user sings a song or writes lyrics, continue the song when appropriate.\n"
#             "If information is unavailable, say so honestly."
#         )
#     }
# ]

# user_input = input("Enter your prompt: ")
# user_prompt = {"role": "user", "content": user_input}
# messages = system_prompt + [user_prompt]

# response = openai_client.responses.create(
#     model="gpt-5-nano",
#     input=messages
# )


# print("\n--- Chatbot Response ---")
# print(response.output_text)


# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()
# client = OpenAI()

# # ---------------------------
# # 1️⃣ SYSTEM PROMPT
# # ---------------------------
# system_prompt = [
#     {
#         "role": "system",
#         "content": (
#             "You are a music-specialized chatbot.\n"
#             "You combine structured music data (artists, genres, albums, songs) "
#             "with conceptual knowledge about music theory, history, and songwriting.\n"
#             "When factual information about artists or songs is required, use provided data.\n"
#             "When explaining concepts, give clear and beginner-friendly explanations.\n"
#             "If the user sings a song or writes lyrics, continue the song when appropriate.\n"
#             "If information is unavailable, say so honestly."
#         )
#     }
# ]

# # ---------------------------
# # 2️⃣ USER PROMPT
# # ---------------------------
# user_input = input("Enter your prompt: ")

# user_prompt = {
#     "role": "user",
#     "content": user_input
# }

# # ---------------------------
# # 3️⃣ COMBINE FOR API
# # ---------------------------
# messages = system_prompt + [user_prompt]

# # ---------------------------
# # 4️⃣ SEND TO OPENAI
# # ---------------------------
# response = client.responses.create(
#     model="gpt-5-nano",
#     input=messages
# )

# print(response.output_text)

# # from dotenv import load_dotenv
# # from openai import OpenAI

# # load_dotenv()
# # client = OpenAI()

# # user_prompt = input("Enter your prompt!!")

# # System_Prompt = [
# #   {
# #     "role": "system",
# #     "content": "You are a music-specialized chatbot.\nYou combine structured music data (artists, genres, albums, songs) with conceptual knowledge about music theory, history, and songwriting.\nWhen factual information about artists or songs is required, use provided data.When explaining concepts, give clear and beginner-friendly explanations.\nIf the user sings a song or writes lyrics, continue the song when appropriate.\nIf information is unavailable, say so honestly."
# #   },
# #   {
# #     "role": "user",
# #     "content": "Explain recursion in simple terms."
# #   }
# # ]

# # UserPrompt = {
# #     "role": "user",
# #     "content": user_prompt
# # }

# # response = client.responses.create(
# #     model = "gpt-5-nano",
# #     input = UserPrompt
# # )

# # print(response.output_text)