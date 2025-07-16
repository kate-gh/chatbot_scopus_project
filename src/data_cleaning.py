import json
from pathlib import Path

def extract_field(data, path_list, default=None):
    """Fonction utilitaire pour extraire un champ imbriqué en toute sécurité."""
    for key in path_list:
        if isinstance(data, dict):
            data = data.get(key, None)
        else:
            return default
    return data if data else default

def normalize_text(text):
    return text.strip().lower() if isinstance(text, str) else ""

def clean_article(raw):
    coredata = raw.get("abstracts-retrieval-response", {})
    article = {}

    # 🆔 Identifiant unique
    scopus_id = extract_field(coredata, ["coredata", "dc:identifier"], "")
    scopus_id = scopus_id.replace("SCOPUS_ID:", "").strip()
    article["scopus_id"] = scopus_id

    article["titre"] = extract_field(coredata, ["coredata", "dc:title"], "").strip()
    article["resume"] = extract_field(coredata, ["coredata", "dc:description"], "").strip()
    article["date_publication"] = extract_field(coredata, ["coredata", "prism:coverDate"], "").strip()
    article["revue"] = extract_field(coredata, ["coredata", "prism:publicationName"], "").strip()
    article["doi"] = extract_field(coredata, ["coredata", "prism:doi"], "").strip()

    # 🔍 Mots-clés : liste de chaînes
    raw_keywords_container = extract_field(coredata, ["authkeywords"], {})
    raw_keywords = raw_keywords_container.get("author-keyword", [])

# uniformiser
    if isinstance(raw_keywords, dict):
        raw_keywords = [raw_keywords]
    elif isinstance(raw_keywords, str):
        raw_keywords = [{"$": raw_keywords}]

    keywords = []
    for kw in raw_keywords:
        if isinstance(kw, dict):
            val = kw.get("$", "").strip()
            if val:
                keywords.append(val)

    article["mots_cles"] = keywords

    # 📚 Domaine de recherche
    subject_areas = extract_field(coredata, ["subject-areas", "subject-area"], [])
    if isinstance(subject_areas, dict):
        article["domaine_recherche"] = subject_areas.get("@abbrev", "")
    elif isinstance(subject_areas, list) and subject_areas:
        article["domaine_recherche"] = subject_areas[0].get("@abbrev", "")
    else:
        article["domaine_recherche"] = ""

    # 👤 AUTEURS
    raw_authors = extract_field(coredata, ["authors", "author"], [])
    if isinstance(raw_authors, str):
        raw_authors = []
    elif isinstance(raw_authors, dict):
        raw_authors = [raw_authors]

    auteurs = []
    for a in raw_authors:
        auteur = {
            "scopus_author_id": a.get("@auid", "").strip(),
            "nom_complet": f"{a.get('ce:given-name', '')} {a.get('ce:surname', '')}".strip(),
            "orcid": a.get("orcid", None),
            "affiliations": []
        }

        # 🏛 AFFILIATIONS
        aff_ids = a.get("affiliation", [])
        if isinstance(aff_ids, dict):
            aff_ids = [aff_ids]
        elif isinstance(aff_ids, str):
            aff_ids = []

        affiliations_block = coredata.get("affiliation", [])
        if isinstance(affiliations_block, dict):
            affiliations_block = [affiliations_block]
        elif isinstance(affiliations_block, str):
            affiliations_block = []

        for aff in aff_ids:
            aff_id = aff.get("@id")
            aff_detail = None
            for affi in affiliations_block:
                if affi.get("@id") == aff_id:
                    aff_detail = {
                        "scopus_affiliation_id": affi.get("@id", ""),
                        "nom_institution": affi.get("affilname", ""),
                        "pays": affi.get("affiliation-country", "")
                    }
                    break
            if aff_detail:
                auteur["affiliations"].append(aff_detail)

        auteurs.append(auteur)

    article["auteurs"] = auteurs

    return article

def main():
    input_path = Path("../data/articles_full.json")
    output_path = Path("../data/articles_clean.json")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    seen_ids = set()
    seen_titles = set()
    cleaned_articles = []

    for raw_article in raw_data:
        try:
            cleaned = clean_article(raw_article)
            scopus_id = cleaned.get("scopus_id", "").strip()
            titre = normalize_text(cleaned.get("titre", ""))

            if not scopus_id and not titre:
                continue

            # 🚫 Supprimer doublons
            if scopus_id in seen_ids or titre in seen_titles:
                continue

            seen_ids.add(scopus_id)
            seen_titles.add(titre)
            cleaned_articles.append(cleaned)

        except Exception as e:
            print(f" Erreur lors du nettoyage d'un article : {e}")

    # ✅ Sauvegarde
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_articles, f, ensure_ascii=False, indent=2)

    print(f" {len(cleaned_articles)} articles nettoyés enregistrés dans {output_path}")

if __name__ == "__main__":
    main()
