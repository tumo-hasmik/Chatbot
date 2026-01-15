from openai import OpenAI

client = OpenAI()

def generate_music_text(track, interpretation):
    prompt = f"""
Explain this song in human terms.

Title: {track['title']}
Artist: {track['artist']}
Tempo: {interpretation['tempo_description']}
Mood: {interpretation['mood']}
Harmony: {interpretation['harmony_description']}

Write:
- Emotional summary
- Best listening context
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
