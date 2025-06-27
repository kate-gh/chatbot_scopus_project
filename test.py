import requests

# Remplace par ta vraie clé API
API_KEY = "c77826d9d77779977c1ab8a027e0746d"

#  Exemple de recherche sur "machine learning"
url = "https://api.elsevier.com/content/search/scopus"
params = {
    "query": "machine learning",
    "count": 5,  # nombre de résultats
    "sort": "relevance"
}
headers = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY
}

# Envoyer la requête
response = requests.get(url, headers=headers, params=params)

#  Lire la réponse
if response.status_code == 200:
    data = response.json()
    results = data.get("search-results", {}).get("entry", [])

    if results:
        for i, entry in enumerate(results, 1):
            print(f" Résultat {i}")
            print("Titre :", entry.get("dc:title", "Non disponible"))
            print("Auteurs :", entry.get("dc:creator", "Non disponible"))
            print("Date de publication :", entry.get("prism:coverDate", "Non disponible"))
            print("DOI :", entry.get("prism:doi", "Non disponible"))
            print("-" * 50)
    else:
        print("Aucun résultat trouvé.")
else:
    print(" Erreur de connexion :", response.status_code)
    print("Message :", response.text)
