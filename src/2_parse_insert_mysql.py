from pathlib import Path
import json
import mysql.connector

#Connexion MySQL
db = mysql.connector.connect(
host="localhost",
user="root",
password="", # Mets ton mot de passe MySQL si besoin
database="chatbot_scopus",
charset="utf8mb4"
)
cursor = db.cursor()

#Charger les articles extraits
with open("../data/articles_raw.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

#Dictionnaires pour éviter les doublons
articles_in_db = {}
auteurs_in_db = {}
affiliations_in_db = {}

for entry in articles:


# --- ARTICLE ---
scopus_id = entry.get("dc:identifier", "").replace("SCOPUS_ID:", "")
titre = entry.get("dc:title", "")
resume = entry.get("dc:description", "")
date_pub = entry.get("prism:coverDate", "")
revue = entry.get("prism:publicationName", "")
doi = entry.get("prism:doi", "")
mots_cles = entry.get("authkeywords", "")
domaines = ", ".join([s.get("$", "") for s in entry.get("subject-area", [])]) if entry.get("subject-area") else ""

if scopus_id not in articles_in_db:
    sql = """
        INSERT INTO articles (scopus_id, titre, resume, date_publication, revue, doi, mots_cles, domaine_recherche)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (scopus_id, titre, resume, date_pub, revue, doi, mots_cles, domaines))
    article_id = cursor.lastrowid
    articles_in_db[scopus_id] = article_id
else:
    article_id = articles_in_db[scopus_id]

# --- AUTEURS ---
for author in entry.get("author", []):
    scopus_author_id = author.get("@auid", "")
    prenom = author.get("preferred-name", {}).get("given-name", "")
    nom = author.get("preferred-name", {}).get("surname", "")
    nom_complet = f"{prenom} {nom}".strip()
    orcid = author.get("orcid", "")
    affil = author.get("affiliation-current", {})
    aff_nom = affil.get("affiliation-name", "")
    aff_id = affil.get("@affiliation-id", "")
    aff_pays = affil.get("affiliation-country", "")

    # Insertion de l'auteur
    if scopus_author_id and scopus_author_id not in auteurs_in_db:
        sql = """
            INSERT INTO auteurs (scopus_author_id, nom_complet, orcid, affiliation_principale)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (scopus_author_id, nom_complet, orcid, aff_nom))
        auteur_id = cursor.lastrowid
        auteurs_in_db[scopus_author_id] = auteur_id
    elif scopus_author_id:
        auteur_id = auteurs_in_db[scopus_author_id]
    else:
        continue

    # Relation article - auteur
    sql = "INSERT INTO article_auteur (article_id, auteur_id) VALUES (%s, %s)"
    cursor.execute(sql, (article_id, auteur_id))

    # Insertion de l'affiliation
    if aff_id and aff_id not in affiliations_in_db:
        sql = """
            INSERT INTO affiliations (nom_institution, pays, scopus_affiliation_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (aff_nom, aff_pays, aff_id))
        affiliation_id = cursor.lastrowid
        affiliations_in_db[aff_id] = affiliation_id
    elif aff_id:
        affiliation_id = affiliations_in_db[aff_id]
    else:
        affiliation_id = None

    # Relation auteur - affiliation
    if affiliation_id:
        sql = "INSERT INTO auteur_affiliation (auteur_id, affiliation_id) VALUES (%s, %s)"
        cursor.execute(sql, (auteur_id, affiliation_id))
Sauvegarde finale
db.commit()
cursor.close()
db.close()
print(" Données nettoyées et insérées dans MySQL.")