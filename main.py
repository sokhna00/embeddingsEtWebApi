from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import openai
from dotenv import load_dotenv

import uuid
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

from fastapi.middleware.cors import CORSMiddleware



load_dotenv()


app = FastAPI(
    title="Service de Récupération Augmentée",
    description="API pour encoder des documents et rechercher les plus pertinents en fonction d'une requête.",
    version="1.0.0"
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle d'embedding
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Chemin du fichier JSON pour stocker les embeddings
EMBEDDINGS_FILE = 'data/embeddings.json'


# Schémas Pydantic pour la validation
class Document(BaseModel):
    documents: List[str]


class Query(BaseModel):
    query: str



# Assurez-vous de configurer votre clé API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.post("/chat", summary="Obtenir une réponse à partir de la requête utilisateur")
def chat(query: Query, top_k: int = 5):
    # Même processus que dans search_documents pour trouver les documents pertinents
    search_results = search_documents(query, top_k)
    relevant_docs = search_results['relevant_documents']

    # Concaténer les textes des documents pertinents
    context = "\n\n".join([doc['text'] for doc in relevant_docs])

    # Créer le prompt pour l'API OpenAI
    prompt = f"Réponds à la question suivante en utilisant les informations ci-dessous :\n\nContexte:\n{context}\n\nQuestion: {query.query}\n\nRéponse:"

    # Appel à l'API OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Choisissez le modèle approprié
        messages=[
            {"role": "system", "content": "Tu es un assistant utile."},  # Optionnel : définir un rôle de système
            {"role": "user", "content": prompt}  # La question de l'utilisateur avec le contexte
        ],
        max_tokens=150,
        temperature=0.7
    )


    answer = response['choices'][0]['message']['content'].strip()

    return {
        "answer": answer
    }


@app.post("/upload_documents", summary="Télécharger des documents à encoder")
async def upload_documents(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier téléchargé.")

    texts = []
    for file in files:
        contents = await file.read()
        text = contents.decode('utf-8')
        texts.append(text)

    # Appeler la fonction d'encodage avec les textes extraits
    encode_documents(Document(documents=texts))

    return {
        "status": "success",
        "message": "Documents téléchargés, encodés et stockés avec succès."
    }


@app.post("/encode_documents", summary="Encoder des documents")
def encode_documents(documents: Document):
    if not documents.documents:
        raise HTTPException(status_code=400, detail="Aucun document fourni.")

    # Vérifier si le fichier existe déjà
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    new_data = []
    for doc in documents.documents:
        doc_id = str(uuid.uuid4())
        embedding = model.encode(doc).tolist()
        new_entry = {
            "id": doc_id,
            "text": doc,
            "embedding": embedding
        }
        new_data.append(new_entry)

    # Combiner les données existantes avec les nouvelles
    combined_data = existing_data + new_data

    # Enregistrer dans le fichier JSON
    with open(EMBEDDINGS_FILE, 'w') as f:
        json.dump(combined_data, f)

    return {
        "status": "success",
        "message": "Documents encodés et stockés avec succès."
    }


@app.post("/search_documents", summary="Rechercher des documents pertinents")
def search_documents(query: Query, top_k: int = 5):
    if not query.query:
        raise HTTPException(status_code=400, detail="Aucune requête fournie.")

    # Vérifier si le fichier d'embeddings existe
    if not os.path.exists(EMBEDDINGS_FILE):
        raise HTTPException(status_code=404, detail="Aucun document encodé trouvé.")

    with open(EMBEDDINGS_FILE, 'r') as f:
        documents = json.load(f)

    # Encoder la requête
    query_embedding = model.encode(query.query)

    # Calculer la similarité cosinus
    similarities = []
    for doc in documents:
        doc_embedding = np.array(doc['embedding'])
        cosine_sim = np.dot(query_embedding, doc_embedding) / (norm(query_embedding) * norm(doc_embedding))
        similarities.append({
            "id": doc['id'],
            "text": doc['text'],
            "similarity_score": float(cosine_sim)
        })

    # Trier les documents par similarité décroissante
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

    return {
        "relevant_documents": similarities[:top_k]
    }
