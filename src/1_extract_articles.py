import requests
import json
import time
from pathlib import Path
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Lire les variables d'environnement
API_KEY = os.getenv("SCOPUS_API_KEY")
INST_TOKEN = os.getenv("INST_TOKEN")

headers = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY,
    "X-ELS-Insttoken": INST_TOKEN
}

query = "machine learning"
search_url = "https://api.elsevier.com/content/search/scopus"
abstract_url = "https://api.elsevier.com/content/abstract/scopus_id/"

articles_basic = []
for start in range(0, 500, 25):
    print(f" Recherche articles {start + 1} à {start + 25}")
    params = {"query": query, "count": 25, "start": start}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        entries = response.json().get("search-results", {}).get("entry", [])
        articles_basic.extend(entries)
    else:
        print(f" Erreur recherche : {response.status_code}")
        break
    time.sleep(1)

print(f" Articles récupérés : {len(articles_basic)}")

# Enrichissement via Abstract Retrieval API
articles_enriched = []
for article in articles_basic:
    scopus_id = article.get("dc:identifier", "").replace("SCOPUS_ID:", "")
    if not scopus_id:
        continue
    url = f"{abstract_url}{scopus_id}?view=FULL"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        articles_enriched.append(data)
    else:
        print(f" Erreur enrichissement ID={scopus_id} : {response.status_code}")
    time.sleep(1)

Path("../data").mkdir(exist_ok=True)

with open("../data/articles_full.json", "w", encoding="utf-8") as f:
    json.dump(articles_enriched, f, ensure_ascii=False, indent=2)

print(" Données enrichies enregistrées.")
