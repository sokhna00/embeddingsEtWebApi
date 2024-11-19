
import requests

# URL de l'API
API_URL = "http://localhost:8000"

# Encodage des documents
documents = {
    "documents": [
        "Article 1 : Toute personne a droit au respect de sa vie privée et familiale, de son domicile et de sa correspondance.",
        "Le climat change, il est temps d'agir.",
        "Je suis très heureux de participer à cette conférence !",
        "L'intelligence artificielle va changer le monde. #IA"
    ]
}

response = requests.post(f"{API_URL}/encode_documents", json=documents)
print(response.json())

# Recherche de documents
query = {
    "query": "Droit à la vie privée"
}

response = requests.post(f"{API_URL}/search_documents", json=query)
print(response.json())
