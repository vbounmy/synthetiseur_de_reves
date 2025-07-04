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
    def do_analysis():
        with st.spinner("Analyse émotionnelle..."):
            analyse = text_analysis(texte)
            st.session_state.analyse = analyse

    if "analyse" not in st.session_state or st.session_state.get("retry_analysis", False):
        try:
            do_analysis()
            st.session_state.retry_analysis = False
        except SDKError as e:
            error_msg = str(e)
            if "429" in error_msg or "capacity" in error_msg.lower():
                st.error("Erreur 429 : capacité dépassée, veuillez réessayer.")
                if st.button("Réessayer l'analyse émotionnelle"):
                    st.session_state.retry_analysis = True
                    st.experimental_rerun()
            else:
                st.error(f"Erreur lors de l'analyse (API Mistral) : {e}")
                st.stop()

    if "analyse" in st.session_state and not st.session_state.get("retry_analysis", False):
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

