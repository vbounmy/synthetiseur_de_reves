from groq import Groq
from mistralai import Mistral
from dotenv import load_dotenv
import os
import json

load_dotenv()

def read_file(text_file_path):
    with open(text_file_path, "r") as file:
        return file.read()

# Open the audio file
def speech_to_text(audio_path, language="fr"):
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    with open(audio_path, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=file, # Required audio file
            model="whisper-large-v3-turbo", # Required model to use for transcription
            prompt="Extrait le texte de l'audio de la manière la plus factuelle possible",  # Optional
            response_format="verbose_json",  # Optional
            timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
            language=language,  # Optional
            temperature=0.0  # Optional
        )
        # To print only the transcription text, you'd use print(transcription.text) (here we're printing the entire transcription object to access timestamps)
        return transcription.text

def text_analysis(text):
    client = Mistral(api_key = os.environ["MISTRAL_API_KEY"])

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": read_file(text_file_path="context_analysis.txt")
            },
            {
                "role": "user",
                "content": f"Analyse le texte ci-dessous (ta réponse doit être dans le format JSON) : {text}",
            },
        ],
        response_format = {"type": "json_object"}
    )

    print(chat_response.choices[0].message.content)

if __name__ == "__main__":
    audio_path = "../nlp_audio.m4a"
    text = speech_to_text(audio_path, language="fr")
    print(text)
    analysis = text_analysis(text)