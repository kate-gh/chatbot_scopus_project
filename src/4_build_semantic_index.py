from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
from pathlib import Path

# Charger les articles nettoyés avec mots-clés
with open("../data/articles_clean.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Choisir le texte à indexer (résumé ou titre)
corpus = []
id_map = []  # pour stocker les index et les associer aux articles
for i, article in enumerate(articles):
    texte = article.get("dc:description", "") or article.get("dc:title", "")
    if texte.strip():
        corpus.append(texte)
        id_map.append(i)  # on garde l'index pour retrouver l'article ensuite

# Encoder les textes avec un modèle BERT
model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = model.encode(corpus, convert_to_numpy=True)

# Construire l’index FAISS
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

# Sauvegarder l’index et les mappings
faiss.write_index(index, "../data/semantic_index.faiss")

# Sauvegarder le mapping index <-> article
with open("../data/id_map.json", "w", encoding="utf-8") as f:
    json.dump(id_map, f, indent=2)

print(" Index vectoriel FAISS généré avec succès.")
