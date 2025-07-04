import streamlit as st
from backend import speech_to_text, text_analysis, text_to_image

st.title("Transformation d'un rêve en une image 💤")

uploaded_audio = st.file_uploader("Charge un fichier audio (format .m4a, .wav...)", type=["m4a", "wav", "mp3"])

if uploaded_audio is not None:
    file_extension = uploaded_audio.name.split('.')[-1]
    temp_file_name = f"temp_audio_file.{file_extension}"
    
    with open(temp_file_name, "wb") as f:
        f.write(uploaded_audio.read())
    
    with st.spinner("Transcription en cours..."):
        texte = speech_to_text(temp_file_name, language="fr")
    st.subheader("Transcription du rêve :")
    st.write(texte)
    
    with st.spinner("Analyse émotionnelle..."):
        analyse = text_analysis(texte)

    # Trier les émotions par score décroissant
    top_2 = sorted(analyse.items(), key=lambda x: x[1], reverse=True)[:2]

    # Formatage en pourcentages
    st.subheader("Top 2 émotions dominantes du rêve :")
    for emotion, score in top_2:
        st.write(f"**{emotion.capitalize()}** : {round(score * 100, 2)}%")

    
    with st.spinner("Génération de l'image..."):
        image_bytes = text_to_image(texte)
    st.subheader("Image générée du rêve :")
    st.image(image_bytes)
