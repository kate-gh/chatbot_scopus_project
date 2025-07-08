from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from app.db import get_connection

def fetch_articles():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, titre, resume FROM articles WHERE resume IS NOT NULL")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()
    return articles

def build_index():
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    articles = fetch_articles()
    abstracts = [a['resume'] for a in articles]
    embeddings = model.encode(abstracts, show_progress_bar=True)
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype('float32'))
    
    return index, articles, model
