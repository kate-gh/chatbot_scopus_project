import json
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chatbot_scopus",
    charset="utf8mb4"
)
cursor = db.cursor()

with open("../data/articles_full.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

articles_in_db = {}
auteurs_in_db = {}
affiliations_in_db = {}
auteurs_affiliations_principales = {}  # Nouveau dictionnaire pour tracer les affiliations principales

def extract_affiliation_id(aff_data):
    """Extrait l'ID d'affiliation de différents champs possibles"""
    if not aff_data:
        return ""
    
    # Essayer différents champs pour l'ID d'affiliation
    possible_fields = ["@afid", "@id", "@affiliation-id", "affiliation-id"]
    
    for field in possible_fields:
        if field in aff_data:
            value = aff_data[field]
            if isinstance(value, dict) and "@afid" in value:
                return str(value["@afid"]).strip()
            elif value:
                return str(value).strip()
    
    return ""

def debug_affiliation_structure(aff_data, author_index=0):
    """Fonction de débogage pour voir la structure des données d'affiliation"""
    print(f"--- Debug Affiliation Author {author_index} ---")
    print(f"Type: {type(aff_data)}")
    print(f"Keys: {list(aff_data.keys()) if isinstance(aff_data, dict) else 'Not a dict'}")
    print(f"Full data: {aff_data}")
    print("--- End Debug ---")

for item_index, item in enumerate(articles):
    try:
        entry = item.get("abstracts-retrieval-response", {})
        core = entry.get("coredata", {})

        scopus_id = core.get("dc:identifier", "").replace("SCOPUS_ID:", "").strip()
        titre = core.get("dc:title", "").strip()
        resume = core.get("dc:description", "").strip()
        date_pub = core.get("prism:coverDate", "").strip()
        revue = core.get("prism:publicationName", "").strip()
        doi = core.get("prism:doi", "").strip()

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

        subject_areas = entry.get("subject-areas")
        if subject_areas is None:
            domaines = ""
        else:
            domaines = subject_areas.get("subject-area", "")
            if isinstance(domaines, list):
                domaines = ", ".join([d.get("$", "").strip() for d in domaines if d.get("$")])
            elif isinstance(domaines, dict):
                domaines = domaines.get("$", "").strip()
            else:
                domaines = ""

        # Insert article si nouveau
        if scopus_id and scopus_id not in articles_in_db:
            sql_article = """
                INSERT INTO articles
                    (scopus_id, titre, resume, date_publication, revue, doi, mots_cles, domaine_recherche)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql_article, (scopus_id, titre, resume, date_pub, revue, doi, mots_cles, domaines))
            article_id = cursor.lastrowid
            articles_in_db[scopus_id] = article_id
        else:
            article_id = articles_in_db.get(scopus_id)

        authors = entry.get("authors", {}).get("author", [])
        if not isinstance(authors, list):
            authors = [authors]

        for author_index, author in enumerate(authors):
            preferred = author.get("preferred-name", {})
            surname = preferred.get("ce:surname") or author.get("ce:surname") or ""
            given = preferred.get("ce:given-name") or author.get("ce:given-name") or ""
            nom_complet = f"{surname} {given}".strip()

            scopus_author_id = author.get("@auid", "").strip()
            orcid = author.get("@orcid") or author.get("orcid") or ""
            orcid = orcid.strip() if orcid else ""

            # Amélioration de l'extraction des affiliations
            aff_data = author.get("affiliation") or author.get("affiliation-current") or {}
            if isinstance(aff_data, list):
                aff_data = aff_data[0] if aff_data else {}

            # Debug pour les premiers articles (optionnel)
            if item_index < 3 and author_index < 2:  # Debug les 3 premiers articles, 2 premiers auteurs
                debug_affiliation_structure(aff_data, author_index)

            aff_name_parts = []
            affiliation_id = None
            
            if aff_data:
                # Extraction améliorée de l'ID d'affiliation
                scopus_aff_id = extract_affiliation_id(aff_data)
                
                # Extraction du nom d'affiliation
                orgs = aff_data.get("organization") or []
                if not isinstance(orgs, list):
                    orgs = [orgs]
                for org in orgs:
                    if isinstance(org, dict) and "$" in org:
                        aff_name_parts.append(org["$"].strip())
                    elif isinstance(org, str):
                        aff_name_parts.append(org.strip())

                if not aff_name_parts:
                    aff_name = aff_data.get("ce:source-text", "").strip()
                    if not aff_name:
                        aff_name = aff_data.get("affilname", "").strip()
                else:
                    aff_name = ", ".join(aff_name_parts)

                pays = aff_data.get("country", "").strip()
                ville = aff_data.get("city", "").strip()
                
                # Affichage pour débogage
                if item_index < 3:
                    print(f"Article {item_index}, Auteur {author_index}:")
                    print(f"  Nom affiliation: '{aff_name}'")
                    print(f"  Scopus Aff ID: '{scopus_aff_id}'")
                    print(f"  Pays: '{pays}', Ville: '{ville}'")
                
                # Insert affiliation si nouveau
                if aff_name:  # S'assurer qu'il y a un nom d'affiliation
                    # Utiliser l'ID Scopus comme clé principale, sinon le nom en minuscules
                    cle_aff = scopus_aff_id if scopus_aff_id else f"name_{aff_name.lower()}"
                    
                    if cle_aff not in affiliations_in_db:
                        sql_aff = """
                            INSERT INTO affiliations (nom_institution, pays, ville, scopus_affiliation_id)
                            VALUES (%s,%s,%s,%s)
                        """
                        cursor.execute(sql_aff, (aff_name, pays, ville, scopus_aff_id if scopus_aff_id else None))
                        affiliation_id = cursor.lastrowid
                        affiliations_in_db[cle_aff] = affiliation_id
                        print(f"  Nouvelle affiliation créée: ID={affiliation_id}")
                    else:
                        affiliation_id = affiliations_in_db.get(cle_aff)
                        print(f"  Affiliation existante: ID={affiliation_id}")

            # Insert auteur si nouveau avec affiliation_principale
            if scopus_author_id and scopus_author_id not in auteurs_in_db:
                sql_auteur = """
                    INSERT INTO auteurs (scopus_author_id, nom_complet, orcid, affiliation_principale)
                    VALUES (%s,%s,%s,%s)
                """
                cursor.execute(sql_auteur, (scopus_author_id, nom_complet, orcid, affiliation_id))
                auteur_id = cursor.lastrowid
                auteurs_in_db[scopus_author_id] = auteur_id
                print(f"  Nouvel auteur créé: {nom_complet}, ID={auteur_id}, Affiliation principale={affiliation_id}")
            else:
                auteur_id = auteurs_in_db.get(scopus_author_id)
                
                # Mettre à jour l'affiliation principale si elle n'est pas définie ET qu'on a une affiliation
                if affiliation_id:
                    # Vérifier si l'auteur a déjà une affiliation principale
                    cursor.execute("SELECT affiliation_principale FROM auteurs WHERE id = %s", (auteur_id,))
                    result = cursor.fetchone()
                    
                    if result and result[0] is None:  # Si affiliation_principale est NULL
                        sql_update = "UPDATE auteurs SET affiliation_principale = %s WHERE id = %s"
                        cursor.execute(sql_update, (affiliation_id, auteur_id))
                        print(f"  Affiliation principale mise à jour pour {nom_complet}: {affiliation_id}")
                    elif result:
                        print(f"  Auteur {nom_complet} a déjà une affiliation principale: {result[0]}")
                        
                print(f"  Auteur existant: {nom_complet}, ID={auteur_id}")
                
            # Tracer l'affiliation principale pour cet auteur (pour mise à jour en fin)
            if scopus_author_id and affiliation_id:
                if scopus_author_id not in auteurs_affiliations_principales:
                    auteurs_affiliations_principales[scopus_author_id] = affiliation_id

            # Lien article-auteur
            if article_id and auteur_id:
                cursor.execute(
                    "INSERT IGNORE INTO article_auteur (article_id, auteur_id) VALUES (%s,%s)",
                    (article_id, auteur_id)
                )

            # Lien auteur-affiliation
            if auteur_id and affiliation_id:
                cursor.execute(
                    "INSERT IGNORE INTO auteur_affiliation (auteur_id, affiliation_id) VALUES (%s,%s)",
                    (auteur_id, affiliation_id)
                )

        # Traitement des affiliations listées directement dans l'article (entry)
        affiliation_list = entry.get("affiliation", [])
        if not isinstance(affiliation_list, list):
            affiliation_list = [affiliation_list]
            
        for aff in affiliation_list:
            if not isinstance(aff, dict):
                continue

            nom_inst = aff.get("affilname", "").strip()
            pays = aff.get("affiliation-country", "").strip()
            ville = aff.get("affiliation-city", "").strip()
            
            # Extraction améliorée de l'ID d'affiliation
            scopus_aff_id = extract_affiliation_id(aff)

            if not nom_inst:
                continue

            cle_aff = scopus_aff_id if scopus_aff_id else f"name_{nom_inst.lower()}"
            if cle_aff not in affiliations_in_db:
                sql_aff = """
                    INSERT INTO affiliations (nom_institution, pays, ville, scopus_affiliation_id)
                    VALUES (%s,%s,%s,%s)
                """
                cursor.execute(sql_aff, (nom_inst, pays, ville, scopus_aff_id if scopus_aff_id else None))
                affiliation_id = cursor.lastrowid
                affiliations_in_db[cle_aff] = affiliation_id
            else:
                affiliation_id = affiliations_in_db[cle_aff]

            # Associer tous les auteurs à cette affiliation
            for author in authors:
                scopus_author_id = author.get("@auid", "").strip()
                auteur_id = auteurs_in_db.get(scopus_author_id)
                if auteur_id and affiliation_id:
                    cursor.execute(
                        "INSERT IGNORE INTO auteur_affiliation (auteur_id, affiliation_id) VALUES (%s,%s)",
                        (auteur_id, affiliation_id)
                    )

    except Exception as e:
        print(f"Erreur lors du traitement de l'article avec SCOPUS_ID={core.get('dc:identifier', '???')}: {e}")

# Mise à jour finale des affiliations principales pour les auteurs qui n'en ont pas
print("\n=== Mise à jour finale des affiliations principales ===")
for scopus_author_id, affiliation_id in auteurs_affiliations_principales.items():
    auteur_id = auteurs_in_db.get(scopus_author_id)
    if auteur_id:
        # Vérifier si l'auteur a une affiliation principale
        cursor.execute("SELECT affiliation_principale FROM auteurs WHERE id = %s", (auteur_id,))
        result = cursor.fetchone()
        
        if result and result[0] is None:  # Si affiliation_principale est NULL
            sql_update = "UPDATE auteurs SET affiliation_principale = %s WHERE id = %s"
            cursor.execute(sql_update, (affiliation_id, auteur_id))
            print(f"Affiliation principale mise à jour pour auteur ID {auteur_id}: {affiliation_id}")

db.commit()
cursor.close()
db.close()

print("Insertion terminée.")