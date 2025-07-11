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

def clean_article(raw):
    coredata = raw.get("abstracts-retrieval-response", {})
    article = {}

    article["scopus_id"] = extract_field(coredata, ["coredata", "dc:identifier"], "").replace("SCOPUS_ID:", "").strip()
    article["titre"] = extract_field(coredata, ["coredata", "dc:title"], "")
    article["resume"] = extract_field(coredata, ["coredata", "dc:description"], "")
    article["date_publication"] = extract_field(coredata, ["coredata", "prism:coverDate"], "")
    article["revue"] = extract_field(coredata, ["coredata", "prism:publicationName"], "")
    article["doi"] = extract_field(coredata, ["coredata", "prism:doi"], "")
    article["mots_cles"] = extract_field(coredata, ["authkeywords"], [])
    if isinstance(article["mots_cles"], str):
        article["mots_cles"] = [article["mots_cles"]]

    article["domaine_recherche"] = extract_field(coredata, ["subject-areas", "subject-area"], [{}])[0].get("@abbrev", "")

    # AUTEURS
    raw_authors = extract_field(coredata, ["authors", "author"], [])
    if not isinstance(raw_authors, list):
        raw_authors = [raw_authors]
    auteurs = []
    for a in raw_authors:
        auteur = {
    "scopus_author_id": a.get("@auid", ""),
    "nom_complet": f"{a.get('ce:given-name', '')} {a.get('ce:surname', '')}".strip(),
    "orcid": a.get("orcid", None),
    "affiliations": []
}

        # AFFILIATIONS
        aff_ids = a.get("affiliation", [])
        if not isinstance(aff_ids, list):
            aff_ids = [aff_ids]
        for aff in aff_ids:
            aff_id = aff.get("@id")
            aff_detail = None
            for affi in coredata.get("affiliation", []):
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

    cleaned_articles = []
    for raw_article in raw_data:
        try:
            cleaned = clean_article(raw_article)
            if cleaned.get("scopus_id"):
                cleaned_articles.append(cleaned)
        except Exception as e:
            print(f"Erreur lors du nettoyage d'un article : {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_articles, f, ensure_ascii=False, indent=2)

    print(f"{len(cleaned_articles)} articles nettoyés enregistrés dans {output_path}")

if __name__ == "__main__":
    main()
