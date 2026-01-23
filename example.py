
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from prompts import system_prompt1
from dotenv import load_dotenv
import os
from supabase import create_client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- Load environment variables ---
load_dotenv()

# --- OpenAI client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Flask app setup ---
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # Enable CORS for browser requests

# --- Spotify client ---
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# --- Supabase client ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Load documents for RAG ---
data = supabase.table("documents").select("*").execute()
documents = data.data or []

sheet_content = "\n".join([
    f"{doc.get('topic', doc.get('title', 'No Title'))}: {doc.get('content', 'No Content')}"
    for doc in documents
])

system_prompt = [
    {"role": "system",
     "content": f"You are a music-specialized chatbot. Use this knowledge:\n{sheet_content}"}
]

# --- Utility: embed text ---
def embed_query(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# --- Utility: semantic search (RAG) ---
def semantic_search(query_text, sb_client) -> list[dict]:
    emb_q = embed_query(query_text)
    res = sb_client.rpc("match_chunks", {"query_embedding": emb_q, "match_count": 5}).execute()
    return res.data or []

# --- Routes ---

# Serve index.html
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Serve static files (CSS, JS)
@app.get("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# Spotify search endpoint
@app.route("/spotify", methods=["POST"])
def spotify_info():
    data = request.get_json()
    query = data.get("artist") or data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    results = sp.search(query, type="artist")  # Could also do track/album if needed
    return jsonify(results)

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "No prompt provided"}), 400

    user_input = data["prompt"]

    # --- RAG: retrieve relevant context ---
    rag_rows = semantic_search(user_input, supabase)
    context = "\n\n".join(
        f"[Source {i+1} | sim={row.get('similarity'):.3f}]\n{row.get('content','')}"
        for i, row in enumerate(rag_rows)
    )

    rag_message = {
        "role": "system",
        "content": (
            "Use the retrieved context below to answer. "
            "If it doesn't contain the answer, say so.\n\n"
            f"RETRIEVED CONTEXT:\n{context if context else '(no matches)'}"
        )
    }

    user_message_obj = {"role": "user", "content": user_input}
    full_message = [rag_message, user_message_obj, system_prompt1]

    # --- Call OpenAI ---
    try:
        response = client.responses.create(
            model="gpt-5-nano",
            input=full_message
        )
        answer = response.output_text
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response": answer})

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True, port=5001)


# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from openai import OpenAI
# from prompts import system_prompt1
# from dotenv import load_dotenv
# import os
# from supabase import create_client
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from flask_cors import CORS


# load_dotenv()

# os.getenv("SPOTIFY_CLIENT_ID")
# os.getenv("SPOTIFY_CLIENT_SECRET")

# client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))


# app = Flask(__name__, static_folder="static", static_url_path="")

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#     client_id=os.getenv("SPOTIFY_CLIENT_ID"),
#     client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
# ))

# results = sp.artist("spotify:artist:1dfeR4HaWDbWqFHLkxsg1d")
# print(results['name'], results['genres'])

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# data = supabase.table("documents").select("*").execute()
# documents = data.data

# print(documents)
# def embed_query(text: str) -> list[float]:
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )

#     return response.data[0].embedding

# sheet_content = "\n".join([
#     f"{doc.get('topic', doc.get('title', 'No Title'))}: {doc.get('content', 'No Content')}"
#     for doc in documents
# ])

# def semantic_search(query_text, sb_client) -> list[dict]:
#     emb_q = embed_query(query_text)
#     res = sb_client.rpc(
#         "match_chunks",
#         {"query_embedding": emb_q, "match_count": 5}
#     ).execute()
#     return res.data or []
# # user_message = input("You: ")

# # response = client.responses.create(
# #     model="gpt-4.1-mini",
# #     input=user_message
# # )

# # assistant_message = response.output_text
# # print("Bot:", assistant_message)
# # user_message = input("You: ")

# # response = client.responses.create(
# #     model="gpt-4.1-mini",
# #     input=user_message
# # )

# # assistant_message = response.output_text
# # print("Bot:", assistant_message)

# # REMOVE these lines:
# user_message = input("You: ")

# response = client.responses.create(
#     model="gpt-4.1-mini",
#     input=user_message
# )

# assistant_message = response.output_text
# print("Bot:", assistant_message)


# # user_message = data.get("message", "")
# rag_rows = semantic_search(user_message, supabase)

# context = "\n\n".join(
#     f"[Source {i+1} | sim={row.get('similarity'):.3f}]\n{row.get('content','')}"
#     for i, row in enumerate(rag_rows)
# )

# rag_message = {
#     "role": "system",
#     "content": (
#         "Use the retrieved context below to answer. If it doesn't contain the answer, say so. \n\n"
#         f"RETRIEVED CONTEXT:\n{context if context else '(no matches)'}" 
#     ) }

# full_user_message = {
#         "role": "user",
#         "content": user_message
#     }

# full_message = [rag_message, full_user_message, system_prompt1]

# resp = client.responses.create(
#         model = "gpt-5-nano",
#         input=full_message
#     )

# # sheet_content = ""
# # for doc in documents:
# #     topic = doc.get('topic') or doc.get('title') or "No Title"
# #     content = doc.get('content') or "No Content"
# #     sheet_content += f"{topic}: {content}\n"


# system_prompt = [
#     {"role": "system",
#      "content": f"You are a music-specialized chatbot. Use this knowledge:\n{sheet_content}"}
# ]



# # takes as input a query, conducts the search, returns context
# def semantic_search(query_text, supabase) -> list[dict]:
#     emb_q = embed_query(query_text)
#     res = supabase.rpc("match_chunks", {"query_embedding": emb_q, "match_count" : 5}).execute()
#     rows = res.data or []
#     # for easier debugging
#     # print("RAG OUTPUT:", rows)
#     return rows

# @app.route("/")
# def index():
#     return send_from_directory("static", "index.html")

# @app.route("/spotify", methods=["POST"])
# def spotify_info():
#     query = request.json.get("artist")  # or song/album
#     results = sp.search(query, type="artist")  # or type="track"
#     return jsonify(results)

# # @app.route("/chat", methods=["GET", "POST"])
# # def chat():
# #     user_input = request.json.get("prompt")
# #     user_prompt = {"role": "user", "content": user_input}
# #     messages = system_prompt + [user_prompt]

# #     response = client.responses.create(model="gpt-5-nano", input=messages)
# #     return jsonify({"response": response.output_text})


# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     if not data or "prompt" not in data:
#         return jsonify({"error": "No prompt provided"}), 400

#     user_input = data["prompt"]

#     messages = system_prompt + [
#         {"role": "user", "content": user_input}
#     ]

#     response = client.responses.create(
#         model="gpt-5-nano",
#         input=messages
#     )

#     return jsonify({"response": response.output_text})


# @app.get("/<path:path>")
# def static_files(path):
#     return send_from_directory("static", path)

# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

# app = Flask(__name__, static_folder="static", static_url_path="")
# CORS(app)















# # @app.get("/")
# # def index():
# #     return send_from_directory("public", "index.html")

# # @app.post("/api/chat")
# # def chat():
# #     data = request.get_json(silent=True) or {}
# #     user_message = data.get("message", "")

# #     # conduct semantic search
# #     rag_rows = semantic_search(user_message)

# #     # fixes our formatting
# #     context = "\n\n".join(
# #         f"[Source {i+1} | sim={row.get('similarity'):.3f}]\n{row.get('content','')}"
# #         for i, row in enumerate(rag_rows)
# #     )

# #     # create the rag prompt
# #     rag_message = {
# #         "role": "system",
# #         "content": (
# #             "Use the retrieved context below to answer. If it doesn't contain the answer, say so. \n\n"
# #             f"RETRIEVED CONTEXT:\n{context if context else '(no matches)'}"
# #         )
# #     }

# #     full_user_message = {
# #         "role": "user",
# #         "content": user_message,
# #     }

# #     full_message = [rag_message, full_user_message, SYSTEM_PROMPT]

# #     resp = client.responses.create(
# #         model="gpt-5-nano",
# #         input=full_message
# #     )
# #     return jsonify({"text": resp.output_text})

# # # Serves /styles.css, /app.js, etc.
# # @app.get("/<path:path>")
# # def static_files(path):
# #     return send_from_directory("public", path)

# # if __name__ == "__main__":
# #     app.run(host="127.0.0.1", port=3000, debug=True)





# # #THIS IS THE NEW VERSION THAT TURNS spotify.py INTO A SMALL FLASK API
# # #HUYS UNEM ARDEN PATRASTA HORS AREV


# # from flask import Flask, request, jsonify, send_from_directory
# # from flask_cors import CORS
# # from openai import OpenAI
# # from dotenv import load_dotenv
# # import os
# # from supabase import create_client
# # import spotipy
# # from spotipy.oauth2 import SpotifyClientCredentials


# # load_dotenv()
# # os.getenv("SPOTIFY_CLIENT_ID")
# # os.getenv("SPOTIFY_CLIENT_SECRET")

# # client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))
# # print(os.environ.get("OPENAI_API_KEY"))


# # app = Flask(__name__, static_folder="static", static_url_path="")

# # sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
# #     client_id=os.getenv("SPOTIFY_CLIENT_ID"),
# #     client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
# # ))

# # results = sp.artist("spotify:artist:1dfeR4HaWDbWqFHLkxsg1d")  # Queen
# # print(results['name'], results['genres'])

# # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # SUPABASE_URL = os.getenv("SUPABASE_URL")
# # SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
# # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # data = supabase.table("documents").select("*").execute()
# # documents = data.data

# # print(documents)

# # sheet_content = "\n".join([
# #     f"{doc.get('topic', doc.get('title', 'No Title'))}: {doc.get('content', 'No Content')}"
# #     for doc in documents
# # ])

# # rag_message = {
# #     "role": "system",
# #     "content": (
# #         "Use the retrieved context below to answer. If it doesn't contain the answer, say so. \n\n"
# #         f"RETRIEVED CONTEXT:\n{context if context else '(no matches)'}"
# #     ) }

# # full_user_message = {
# #         "role": "user",
# #         "content": user_message
# #     }

# # full_message = [rag_message, full_user_message, system_prompt]

# # resp = client.responses.create(
# #         model = "gpt-5-nano",
# #         input=full_message
# #     )

# # # sheet_content = ""
# # # for doc in documents:
# # #     topic = doc.get('topic') or doc.get('title') or "No Title"
# # #     content = doc.get('content') or "No Content"
# # #     sheet_content += f"{topic}: {content}\n"


# # system_prompt = [
# #     {"role": "system",
# #      "content": f"You are a music-specialized chatbot. Use this knowledge:\n{sheet_content}"}
# # ]

# # @app.route("/")
# # def index():
# #     return send_from_directory("static", "index.html")

# # @app.route("/spotify", methods=["POST"])
# # def spotify_info():
# #     query = request.json.get("artist")  # or song/album
# #     results = sp.search(query, type="artist")  # or type="track"
# #     return jsonify(results)

# # @app.route("/chat", methods=["GET", "POST"])
# # def chat():
# #     user_input = request.json.get("prompt")
# #     user_prompt = {"role": "user", "content": user_input}
# #     messages = system_prompt + [user_prompt]

# #     response = client.responses.create(model="gpt-5-nano", input=messages)
# #     return jsonify({"response": response.output_text})

# # @app.get("/<path:path>")
# # def static_files(path):
# #     return send_from_directory("static", path)

# # if __name__ == "__main__":
# #     app.run(debug=True, port=5001)


# # THIS IS THE OLD VERSION WITHOUT FLASK
# # 
# # 
# # 
# # from dotenv import load_dotenv
# # from openai import OpenAI
# # from supabase import create_client
# # import os

# # load_dotenv()

# # SUPABASE_URL = os.getenv("SUPABASE_URL")
# # SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
# # openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # data = supabase.table("documents").select("*").execute()
# # documents = data.data  


# # sheet_content = "\n".join([f"{doc['topic']}: {doc['content']}" for doc in documents])

# # system_prompt = [
# #     {
# #         "role": "system",
# #         "content": (
# #             "You are a music-specialized chatbot.\n"
# #             "You combine structured music data (artists, genres, albums, songs) with conceptual knowledge about music theory, history, and songwriting.\n"
# #             "Use the following knowledge as your reference:\n"
# #             f"{sheet_content}\n"
# #             "When factual information about artists or songs is required, use provided data.\n"
# #             "When explaining concepts, give clear and beginner-friendly explanations.\n"
# #             "If the user sings a song or writes lyrics, continue the song when appropriate.\n"
# #             "If information is unavailable, say so honestly."
# #         )
# #     }
# # ]

# # user_input = input("Enter your prompt: ")
# # user_prompt = {"role": "user", "content": user_input}
# # messages = system_prompt + [user_prompt]

# # response = openai_client.responses.create(
# #     model="gpt-5-nano",
# #     input=messages
# # )


# # print("\n--- Chatbot Response ---")
# # print(response.output_text)


# # from dotenv import load_dotenv
# # from openai import OpenAI

# # load_dotenv()
# # client = OpenAI()

# # # ---------------------------
# # # 1️⃣ SYSTEM PROMPT
# # # ---------------------------
# # system_prompt = [
# #     {
# #         "role": "system",
# #         "content": (
# #             "You are a music-specialized chatbot.\n"
# #             "You combine structured music data (artists, genres, albums, songs) "
# #             "with conceptual knowledge about music theory, history, and songwriting.\n"
# #             "When factual information about artists or songs is required, use provided data.\n"
# #             "When explaining concepts, give clear and beginner-friendly explanations.\n"
# #             "If the user sings a song or writes lyrics, continue the song when appropriate.\n"
# #             "If information is unavailable, say so honestly."
# #         )
# #     }
# # ]

# # # ---------------------------
# # # 2️⃣ USER PROMPT
# # # ---------------------------
# # user_input = input("Enter your prompt: ")

# # user_prompt = {
# #     "role": "user",
# #     "content": user_input
# # }

# # # ---------------------------
# # # 3️⃣ COMBINE FOR API
# # # ---------------------------
# # messages = system_prompt + [user_prompt]

# # # ---------------------------
# # # 4️⃣ SEND TO OPENAI
# # # ---------------------------
# # response = client.responses.create(
# #     model="gpt-5-nano",
# #     input=messages
# # )

# # print(response.output_text)

# # # from dotenv import load_dotenv
# # # from openai import OpenAI

# # # load_dotenv()
# # # client = OpenAI()

# # # user_prompt = input("Enter your prompt!!")

# # # System_Prompt = [
# # #   {
# # #     "role": "system",
# # #     "content": "You are a music-specialized chatbot.\nYou combine structured music data (artists, genres, albums, songs) with conceptual knowledge about music theory, history, and songwriting.\nWhen factual information about artists or songs is required, use provided data.When explaining concepts, give clear and beginner-friendly explanations.\nIf the user sings a song or writes lyrics, continue the song when appropriate.\nIf information is unavailable, say so honestly."
# # #   },
# # #   {
# # #     "role": "user",
# # #     "content": "Explain recursion in simple terms."
# # #   }
# # # ]

# # # UserPrompt = {
# # #     "role": "user",
# # #     "content": user_prompt
# # # }

# # # response = client.responses.create(
# # #     model = "gpt-5-nano",
# # #     input = UserPrompt
# # # )

# # # print(response.output_text)