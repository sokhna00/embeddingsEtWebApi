import requests

API_URL = "http://localhost:8000"

documents = {
    "documents": [
        "Article 1 : Toute personne a droit au respect de sa vie privée et familiale, de son domicile et de sa correspondance.",
        "Le climat change, il est temps d'agir."
    ]
}

response = requests.post(f"{API_URL}/encode_documents", json=documents)
print(response.json())
