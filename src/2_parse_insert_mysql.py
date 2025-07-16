import json
import mysql.connector

# Connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chatbot_scopus",
    charset="utf8mb4"
)
cursor = db.cursor()

# Charger les données nettoyées
with open("../data/articles_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Caches pour éviter les doublons
articles_in_db = {}
auteurs_in_db = {}
affiliations_in_db = {}

# Traitement des articles
for article in data:
    try:
        scopus_id = (article.get("scopus_id") or "").strip()
        if not scopus_id:
            continue

        titre = (article.get("titre") or "").strip()
        resume = (article.get("resume") or "").strip()
        date_pub = (article.get("date_publication") or "").strip()
        revue = (article.get("revue") or "").strip()
        doi = (article.get("doi") or "").strip()
        domaine = (article.get("domaine_recherche") or "").strip()

        # mots_cles peut être une liste ou une string
        mots_cles_raw = article.get("mots_cles", [])

        if isinstance(mots_cles_raw, str):
           mots_cles_str = mots_cles_raw.strip()
        elif isinstance(mots_cles_raw, list):
          mots_cles_str = ", ".join(
        kw.get("$", "").strip() if isinstance(kw, dict) else kw.strip()
        for kw in mots_cles_raw if isinstance(kw, (dict, str))
    )
        else:
          mots_cles_str = ""

        # Insertion article
        if scopus_id not in articles_in_db:
            cursor.execute("""
                INSERT INTO articles (scopus_id, titre, resume, date_publication, revue, doi, mots_cles, domaine_recherche)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (scopus_id, titre, resume, date_pub, revue, doi, mots_cles_str, domaine))
            article_id = cursor.lastrowid
            articles_in_db[scopus_id] = article_id
        else:
            article_id = articles_in_db[scopus_id]

        # Traitement des auteurs
        auteurs = article.get("auteurs", [])
        for auteur in auteurs:
            scopus_author_id = str(auteur.get("scopus_author_id", "")).strip()
            nom_complet = (auteur.get("nom_complet") or "").strip()
            orcid = auteur.get("orcid")

            # Insertion auteur
            if scopus_author_id not in auteurs_in_db:
                cursor.execute("""
                    INSERT INTO auteurs (scopus_author_id, nom_complet, orcid, affiliation_principale)
                    VALUES (%s,%s,%s,%s)
                """, (scopus_author_id, nom_complet, orcid, None))
                auteur_id = cursor.lastrowid
                auteurs_in_db[scopus_author_id] = auteur_id
            else:
                auteur_id = auteurs_in_db[scopus_author_id]

            # Traitement affiliations
            affiliations = auteur.get("affiliations", [])
            aff_principale_id = None
            for aff in affiliations:
                aff_id = (aff.get("scopus_affiliation_id") or "").strip()
                nom_inst = (aff.get("nom_institution") or "").strip()
                pays = (aff.get("pays") or "").strip()

                cle_aff = aff_id or nom_inst.lower()
                if cle_aff not in affiliations_in_db:
                    cursor.execute("""
                        INSERT INTO affiliations (nom_institution, pays, scopus_affiliation_id)
                        VALUES (%s,%s,%s)
                    """, (nom_inst, pays, aff_id if aff_id else None))
                    affiliation_id = cursor.lastrowid
                    affiliations_in_db[cle_aff] = affiliation_id
                else:
                    affiliation_id = affiliations_in_db[cle_aff]

                # Lier auteur <-> affiliation
                cursor.execute("""
                    INSERT IGNORE INTO auteur_affiliation (auteur_id, affiliation_id)
                    VALUES (%s,%s)
                """, (auteur_id, affiliation_id))

                if aff_principale_id is None:
                    aff_principale_id = affiliation_id

            # Mettre à jour affiliation principale
            if aff_principale_id:
                cursor.execute("SELECT affiliation_principale FROM auteurs WHERE id=%s", (auteur_id,))
                res = cursor.fetchone()
                if res and not res[0]:
                    cursor.execute("UPDATE auteurs SET affiliation_principale = %s WHERE id = %s",
                                   (aff_principale_id, auteur_id))

            # Lier article <-> auteur
            cursor.execute("""
                INSERT IGNORE INTO article_auteur (article_id, auteur_id)
                VALUES (%s,%s)
            """, (article_id, auteur_id))

    except Exception as e:
        print(f"❌ Erreur pour article {article.get('scopus_id', '???')}: {e}")

# Finaliser
db.commit()
cursor.close()
db.close()
print(" Insertion terminée avec succès.")
