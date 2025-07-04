from groq import Groq
from mistralai import Mistral
from dotenv import load_dotenv
import os
import json
import math
import requests

load_dotenv()

def read_file(text_file_path):
    with open(text_file_path, "r") as file:
        return file.read()
    
def softmax(predictions):
    output = {}
    for sentiment, predicted_value in predictions.items():
        output[sentiment] = math.exp(predicted_value*10) / sum([math.exp(value*10) for value in predictions.values()])
    return output

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
        response_format = "json_object"
    )
    predictions = json.loads(chat_response.choices[0].message.content)
    return softmax(predictions)

def text_to_image(text):
    api_key = os.environ.get("CLIPDROP_API_KEY")
    if not api_key:
        raise ValueError("La clé API ClipDrop n'est pas définie dans les variables d'environnement")

    response = requests.post(
        'https://clipdrop-api.co/text-to-image/v1',
        files={
            'prompt': (None, text, 'text/plain')
        },
        headers={
            'x-api-key': api_key
        }
    )

    if response.ok:
        return response.content
    else:
        response.raise_for_status()


# if __name__ == "__main__":
#     audio_path = "../nlp_audio.m4a"
#     text = speech_to_text(audio_path, language="fr")
#     print("Transcription du rêve : ", text)

#     analysis = text_analysis(text)
#     print("Analyse émotionnelle : ", analysis)

#     image_bytes = text_to_image(text)
#     with open("dream_image.png", "wb") as f:
#         f.write(image_bytes)
#     print("Image générée sauvegardée sous dream_image.png")