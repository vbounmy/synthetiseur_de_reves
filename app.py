import streamlit as st
from backend import speech_to_text, text_analysis, text_to_image
from mistralai.models.sdkerror import SDKError

st.title("Transformation d'un rêve en une image 💤")

uploaded_audio = st.file_uploader("Charge un fichier audio (format .m4a, .wav...)", type=["m4a", "wav", "mp3"])

if uploaded_audio is not None:
    file_extension = uploaded_audio.name.split('.')[-1]
    temp_file_name = f"temp_audio_file.{file_extension}"

    # Sauvegarde temporaire
    with open(temp_file_name, "wb") as f:
        f.write(uploaded_audio.read())

    # Transcription
    if "texte" not in st.session_state:
        with st.spinner("Transcription en cours..."):
            st.session_state.texte = speech_to_text(temp_file_name, language="fr")
        st.success("Transcription terminée ✅")

    st.subheader("Transcription du rêve :")
    st.write(st.session_state.texte)

    # Analyse émotionnelle avec gestion d'erreur
    if "analyse" not in st.session_state or st.button("🔁 Réanalyser le rêve"):
        try:
            with st.spinner("Analyse émotionnelle en cours..."):
                st.session_state.analyse = text_analysis(st.session_state.texte)
        except SDKError as e:
            st.error(f"Erreur lors de l'analyse (API Mistral) : {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"Erreur inattendue lors de l'analyse : {str(e)}")
            st.stop()

    # Affichage des deux émotions principales
    if "analyse" in st.session_state:
        top_2 = sorted(st.session_state.analyse.items(), key=lambda x: x[1], reverse=True)[:2]
        st.subheader("Top 2 émotions dominantes du rêve :")
        for emotion, score in top_2:
            st.write(f"**{emotion.capitalize()}** : {round(score * 100, 2)}%")

    # Génération d'image avec bouton de relance
    if "image" not in st.session_state or st.button("🔁 Régénérer l'image du rêve"):
        try:
            with st.spinner("Génération de l'image..."):
                st.session_state.image = text_to_image(st.session_state.texte)
        except Exception as e:
            st.error(f"Erreur lors de la génération d'image : {str(e)}")
            st.stop()

    if "image" in st.session_state:
        st.subheader("Image générée du rêve :")
        st.image(st.session_state.image)

