import requests
import json
import time
from pathlib import Path
	#8879c883ce16febb4846c624f21596fa omaima ucd
    #c77826d9d77779977c1ab8a027e0746d kawtar
API_KEY = "8879c883ce16febb4846c624f21596fa"
headers = {"Accept": "application/json", "X-ELS-APIKey": API_KEY}
query = "machine learning"
url = "https://api.elsevier.com/content/search/scopus"

articles = []
for start in range(0, 500, 25):
    print(f" Récupération {start + 1} à {start + 25}")
    params = {"query": query, "count": 25, "start": start}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        entries = data.get("search-results", {}).get("entry", [])
        articles.extend(entries)
    else:
        print(f" Erreur {response.status_code}")
        break
    time.sleep(1)

Path("data").mkdir(exist_ok=True)
print(f"Nombre total d’articles collectés : {len(articles)}")

# Est-ce que la liste contient bien des dictionnaires ?
if len(articles) > 0:
    print(" Exemple du premier article :")
    print(json.dumps(articles[0], indent=2, ensure_ascii=False))
else:
    print(" Aucun article collecté")


with open("../data/articles_raw.json", "w", encoding="utf-8") as f:
    try:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        print(" Enregistrement JSON terminé.")
    except Exception as e:
        print(" Erreur lors de l’enregistrement JSON :", e)


print(f" {len(articles)} articles enregistrés.")