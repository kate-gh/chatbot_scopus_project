from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
from pathlib import Path

# Charger les articles nettoyés avec mots-clés
try:
    with open("../data/articles_clean.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"Articles chargés : {len(articles)}")
except FileNotFoundError:
    print("Erreur : Le fichier articles_clean.json n'existe pas.")
    print("Assurez-vous d'avoir exécuté 3_clean_keywords.py avant.")
    exit(1)

# Choisir le texte à indexer (résumé ou titre)
corpus = []
id_map = []  # pour stocker les index et les associer aux articles

for i, article in enumerate(articles):
    # Extraire le texte depuis la structure Scopus
    if isinstance(article, dict) and "abstracts-retrieval-response" in article:
        core = article.get("abstracts-retrieval-response", {}).get("coredata", {})
        texte = core.get("dc:description", "") or core.get("dc:title", "")
    elif isinstance(article, dict):
        # Si c'est un dict direct (fallback)
        texte = article.get("dc:description", "") or article.get("dc:title", "")
    else:
        texte = ""
    
    if texte and texte.strip():
        corpus.append(texte.strip())
        id_map.append(i)

print(f"Textes valides trouvés : {len(corpus)}")

# Vérifier si on a des textes à indexer
if len(corpus) == 0:
    print("Erreur : Aucun texte valide trouvé pour l'indexation.")
    print("Vérifiez la structure de vos données JSON.")
    
    # Debug : afficher quelques exemples
    print("\nExemples d'articles (premiers 3) :")
    for i, article in enumerate(articles[:3]):
        print(f"Article {i}: {type(article)}")
        if isinstance(article, dict):
            print(f"  Clés disponibles: {list(article.keys())[:10]}")
            if "abstracts-retrieval-response" in article:
                core = article["abstracts-retrieval-response"].get("coredata", {})
                print(f"  Titre: {core.get('dc:title', 'N/A')[:100]}...")
                print(f"  Résumé: {core.get('dc:description', 'N/A')[:100]}...")
            else:
                print(f"  Titre: {article.get('dc:title', 'N/A')[:100]}...")
                print(f"  Résumé: {article.get('dc:description', 'N/A')[:100]}...")
    exit(1)

# Encoder les textes avec un modèle BERT
print("Chargement du modèle BERT...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Encodage des textes...")
vectors = model.encode(corpus, convert_to_numpy=True)

print(f"Forme des vecteurs : {vectors.shape}")

# Vérifier la forme des vecteurs
if len(vectors.shape) != 2 or vectors.shape[0] == 0:
    print(f"Erreur : Forme inattendue des vecteurs : {vectors.shape}")
    exit(1)

# Construire l'index FAISS
print("Construction de l'index FAISS...")
index = faiss.IndexFlatL2(vectors.shape[1])
index.add(vectors)

# Créer le dossier data s'il n'existe pas
Path("../data").mkdir(exist_ok=True)

# Sauvegarder l'index et les mappings
faiss.write_index(index, "../data/semantic_index.faiss")

# Sauvegarder le mapping index <-> article
with open("../data/id_map.json", "w", encoding="utf-8") as f:
    json.dump(id_map, f, indent=2)

print(f"Index vectoriel FAISS généré avec succès.")
print(f"Nombre de vecteurs indexés : {vectors.shape[0]}")
print(f"Dimension des vecteurs : {vectors.shape[1]}")

# Test de l'index
print("\nTest de l'index...")
test_query = "machine learning"
query_vector = model.encode([test_query], convert_to_numpy=True)
distances, indices = index.search(query_vector, 5)

print(f"Recherche pour '{test_query}' :")
for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    if idx < len(id_map):
        article_idx = id_map[idx]
        if article_idx < len(articles):
            article = articles[article_idx]
            if isinstance(article, dict) and "abstracts-retrieval-response" in article:
                core = article["abstracts-retrieval-response"].get("coredata", {})
                titre = core.get("dc:title", "Titre non disponible")
            else:
                titre = article.get("dc:title", "Titre non disponible")
            print(f"  {i+1}. Distance: {dist:.4f} - {titre[:80]}...")