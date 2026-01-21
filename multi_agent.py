from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt1, system_prompt2
import os
from supabase import create_client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

FIRST_SUPABASE_URL = os.getenv("FIRST_SUPABASE_URL")
FIRST_SUPABASE_KEY = os.getenv("FIRST_SUPABASE_SERVICE_ROLE_KEY")
supabase1 = create_client(FIRST_SUPABASE_URL, FIRST_SUPABASE_KEY)

SECOND_SUPABASE_URL = os.getenv("SECOND_SUPABASE_URL")
SECOND_SUPABASE_KEY = os.getenv("SECOND_SUPABASE_SERVICE_ROLE_KEY")
supabase2 = create_client(SECOND_SUPABASE_URL, SECOND_SUPABASE_KEY)

client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))

# sheet_content = "\n".join([
#     f"{doc.get('topic', doc.get('title', 'No Title'))}: {doc.get('content', 'No Content')}"
#     for doc in documents
# ])
                
# takes in the string and outputs a vector
def embed_query(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

# takes as input a query, conducts the search, returns context
def semantic_search(query_text, sb_client) -> list[dict]:
    emb_q = embed_query(query_text)
    res = sb_client.rpc(
        "match_chunks",
        {"query_embedding": emb_q, "match_count": 5}
    ).execute()
    return res.data or []

def run_bot(user_message, system_prompt, sb_client) -> str:
    rag_rows = semantic_search(user_message, sb_client)

    # fixes our formatting
    context = "\n\n".join(
        f"[Source {i+1} | sim={row.get('similarity'):.3f}]\n{row.get('content','')}"
        for i, row in enumerate(rag_rows)
    )

    # create the rag prompt
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

    return resp.output_text

def chatbotone(user_message):
    return run_bot(user_message, system_prompt1, supabase1)

def chatbotwo(user_message):
    return run_bot(user_message, system_prompt2, supabase2)

def simulation():
    #contain the output at any given time
    output = chatbotone("Ask a question about something that interests you.")
    print("Chatbotone says:" + output)

    for _ in range(5):
        output = chatbotwo(output)
        print("Chatbotwo says:" + output)

        output = chatbotone(output)
        print("Chatbotone says:" + output)

simulation()
        
