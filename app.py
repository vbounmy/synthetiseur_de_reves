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
            analyse = text_analysis(st.session_state.texte)
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

    # Affichage visuel complet de toutes les émotions
    if "analyse" in st.session_state and not st.session_state.get("retry_analysis", False):
        st.subheader("Analyse émotionnelle complète du rêve :")

        # Couleurs associées à chaque émotion (à ajuster si tu veux)
        emotion_colors = {
            "heureux": "#f4d35e",
            "anxieux": "#4361ee",
            "triste": "#720026",
            "en_colere": "#ef233c",
            "fatigue": "#999999",
            "apeure": "#3a86ff",
        }

        # Affiche chaque émotion avec une barre et le pourcentage
        for emotion, score in sorted(st.session_state.analyse.items(), key=lambda x: x[1], reverse=True):
            color = emotion_colors.get(emotion, "#bbbbbb")
            bar_html = f"""
            <div style='background-color:#ddd; border-radius:5px; width:100%; height:20px; margin-bottom:8px;'>
                <div style='background-color:{color}; width:{score*100}%; height:100%; border-radius:5px;'></div>
            </div>
            """
            st.markdown(f"**{emotion.replace('_', ' ').capitalize()}** : {round(score * 100, 2)}%")
            st.markdown(bar_html, unsafe_allow_html=True)

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




