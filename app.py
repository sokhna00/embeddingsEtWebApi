import streamlit as st
import requests

# URL de l'API backend
API_URL = "http://localhost:8000"

st.title("AntaBot")

# Étape 1 : Télécharger des documents
st.header("1. Télécharger des documents à encoder")
uploaded_files = st.file_uploader("Choisissez des fichiers texte", accept_multiple_files=True, type=['txt'])

if st.button("Encoder les documents"):
    if uploaded_files:
        files = [('files', (file.name, file.getvalue(), file.type)) for file in uploaded_files]
        response = requests.post(f"{API_URL}/upload_documents", files=files)
        if response.status_code == 200:
            st.success("Documents encodés et stockés avec succès.")
        else:
            st.error("Une erreur est survenue lors de l'encodage des documents.")
    else:
        st.warning("Veuillez sélectionner au moins un fichier.")

# Étape 2 : Interagir avec le chatbot
st.header("2. Posez votre question")
user_question = st.text_input("Votre question :")

if st.button("Obtenir une réponse"):
    if user_question:
        payload = {"query": user_question}
        response = requests.post(f"{API_URL}/chat", json=payload)
        if response.status_code == 200:
            answer = response.json()['answer']
            st.markdown("### Réponse :")
            st.write(answer)
        else:
            st.error("Une erreur est survenue lors de la génération de la réponse.")
    else:
        st.warning("Veuillez entrer une question.")
