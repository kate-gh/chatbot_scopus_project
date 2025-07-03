from keybert import KeyBERT
import json

kw_model = KeyBERT()

with open("../data/articles_raw.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

for article in articles:
    mots_cles = article.get("authkeywords", "")
    titre = article.get("dc:title", "")
    resume = article.get("dc:description", "")
    texte = resume if resume else titre

    if not mots_cles and texte:
        keywords = kw_model.extract_keywords(texte, top_n=5)
        mots_cles_gen = [kw[0] for kw in keywords]
        article["authkeywords"] = "; ".join(mots_cles_gen)

with open("../data/articles_clean.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(" Mots-clés générés automatiquement depuis résumé ou titre.")
