from pathlib import Path
import json
import mysql.connector

# 1) Connexion à MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",           # <‐ votre mot de passe MySQL
    database="chatbot_scopus",
    charset="utf8mb4"
)
cursor = db.cursor()

# 2) Charger les articles extraits
with open("../data/articles_raw.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# 3) Dictionnaires pour éviter les doublons en mémoire
articles_in_db     = {}
auteurs_in_db      = {}
affiliations_in_db = {}

for entry in articles:
    # ─── ARTICLES ─────────────────────────────────────────
    scopus_id = entry.get("dc:identifier", "").replace("SCOPUS_ID:", "")
    titre      = entry.get("dc:title", "")
    resume     = entry.get("dc:description", "")
    date_pub   = entry.get("prism:coverDate", "")
    revue      = entry.get("prism:publicationName", "")
    doi        = entry.get("prism:doi", "")
    mots_cles  = entry.get("authkeywords", "")
    domaines   = ", ".join(
        [s.get("$", "") for s in entry.get("subject-area", [])]
    ) if entry.get("subject-area") else ""

    if scopus_id not in articles_in_db:
        sql = """
            INSERT INTO articles
              (scopus_id, titre, resume, date_publication, revue, doi, mots_cles, domaine_recherche)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (
            scopus_id, titre, resume, date_pub,
            revue, doi, mots_cles, domaines
        ))
        article_id = cursor.lastrowid
        articles_in_db[scopus_id] = article_id
    else:
        article_id = articles_in_db[scopus_id]

    # ─── AUTEUR PRINCIPAL (dc:creator) ───────────────────
    dc_creator = entry.get("dc:creator", "").strip()
    if dc_creator:
        nom_complet      = dc_creator
        scopus_author_id = None
        orcid            = ""
        # on utilisera l'affiliation principale comme 'affiliation_principale'
        # (on continue à gérer toutes les affiliations plus bas)
        aff_principale = ""
        # insérer l'auteur s'il est nouveau
        if nom_complet not in auteurs_in_db:
            sql = """
                INSERT INTO auteurs
                  (scopus_author_id, nom_complet, orcid, affiliation_principale)
                VALUES (%s,%s,%s,%s)
            """
            cursor.execute(sql, (
                scopus_author_id,
                nom_complet,
                orcid,
                aff_principale
            ))
            auteur_id = cursor.lastrowid
            auteurs_in_db[nom_complet] = auteur_id
        else:
            auteur_id = auteurs_in_db[nom_complet]

        # lien article↔auteur
        cursor.execute(
            "INSERT INTO article_auteur (article_id, auteur_id) VALUES (%s,%s)",
            (article_id, auteur_id)
        )

        # ─── AFFILIATIONS (toutes celles listées) ───────────
        for aff in entry.get("affiliation", []):
            nom_inst = aff.get("affilname")
            nom_inst = nom_inst.strip() if nom_inst else ""
            pays = aff.get("affiliation-country")
            pays = pays.strip() if pays else ""
            if not nom_inst:
                continue
            # insérer l'institution si nouvelle
            if nom_inst not in affiliations_in_db:
                sql = """
                    INSERT INTO affiliations
                      (nom_institution, pays, scopus_affiliation_id)
                    VALUES (%s,%s,%s)
                """
                cursor.execute(sql, (nom_inst, pays, None))
                affiliation_id = cursor.lastrowid
                affiliations_in_db[nom_inst] = affiliation_id
            else:
                affiliation_id = affiliations_in_db[nom_inst]

            # lien auteur↔affiliation
            cursor.execute(
                "INSERT INTO auteur_affiliation (auteur_id, affiliation_id) VALUES (%s,%s)",
                (auteur_id, affiliation_id)
            )

# 4) Commit & fermer la connexion
db.commit()
cursor.close()
db.close()

print(" Toutes les tables ont été remplies avec articles, auteurs, affiliations et leurs relations.")
