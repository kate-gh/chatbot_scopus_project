import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
from collections import Counter

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "chatbot_scopus")
    )

def get_publications_by_year():
    conn = get_connection()
    query = """
        SELECT 
            LEFT(date_publication, 4) AS year, 
            COUNT(*) AS total 
        FROM articles 
        WHERE LEFT(date_publication, 4) REGEXP '^[0-9]{4}$'
        GROUP BY year 
        ORDER BY year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_publications_by_domain():
    conn = get_connection()
    query = """
        SELECT domaine_recherche, COUNT(*) AS total 
        FROM articles 
        WHERE domaine_recherche IS NOT NULL AND domaine_recherche != ''
        GROUP BY domaine_recherche 
        ORDER BY total DESC 
        LIMIT 10
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_all_keywords():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mots_cles FROM articles WHERE mots_cles IS NOT NULL AND mots_cles != ''")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    all_keywords = []
    for row in rows:
        keywords = row[0].split(';')
        all_keywords.extend([kw.strip().lower() for kw in keywords if kw.strip()])
    return all_keywords
