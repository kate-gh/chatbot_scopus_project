from keybert import KeyBERT
import json

kw_model = KeyBERT()

# Charger les articles depuis le fichier généré par 1_extract_articles.py
with open("../data/articles_full.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f"Articles chargés : {len(articles)}")

for i, article in enumerate(articles):
    try:
        # Extraire les données depuis la structure Scopus
        entry = article.get("abstracts-retrieval-response", {})
        core = entry.get("coredata", {})
        
        # Extraire les mots-clés existants
        authkeywords = entry.get("authkeywords")
        if authkeywords is None:
            mots_cles = ""
        else:
            mots_cles = authkeywords.get("author-keyword", "")
            if isinstance(mots_cles, list):
                mots_cles = ", ".join([k.get("$", "").strip() for k in mots_cles if k.get("$")])
            elif isinstance(mots_cles, dict):
                mots_cles = mots_cles.get("$", "").strip()
            else:
                mots_cles = ""
        
        # Extraire titre et résumé
        titre = core.get("dc:title", "")
        resume = core.get("dc:description", "")
        texte = resume if resume else titre
        
        # Générer des mots-clés automatiquement si manquants
        if not mots_cles and texte:
            try:
                keywords = kw_model.extract_keywords(texte, top_n=5)
                mots_cles_gen = [kw[0] for kw in keywords]
                
                # Ajouter les mots-clés générés à la structure
                if "authkeywords" not in entry:
                    entry["authkeywords"] = {}
                
                # Créer la structure des mots-clés
                entry["authkeywords"]["author-keyword"] = [
                    {"$": kw} for kw in mots_cles_gen
                ]
                
                print(f"Article {i+1}: Mots-clés générés - {', '.join(mots_cles_gen)}")
                
            except Exception as e:
                print(f"Erreur lors de la génération des mots-clés pour l'article {i+1}: {e}")
        elif mots_cles:
            print(f"Article {i+1}: Mots-clés existants - {mots_cles[:100]}...")
        else:
            print(f"Article {i+1}: Pas de texte disponible pour générer des mots-clés")
            
    except Exception as e:
        print(f"Erreur lors du traitement de l'article {i+1}: {e}")

# Sauvegarder les articles avec mots-clés enrichis
with open("../data/articles_clean.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print("Mots-clés générés automatiquement depuis résumé ou titre.")
print("Fichier sauvegardé : ../data/articles_clean.json")