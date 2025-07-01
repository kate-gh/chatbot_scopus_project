import streamlit as st
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Charger les fichiers
with open("../data/articles_clean.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

id_map = json.load(open("../data/id_map.json", "r", encoding="utf-8"))
index = faiss.read_index("../data/semantic_index.faiss")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Interface utilisateur
st.set_page_config(page_title="Chatbot Scopus", layout="wide")
st.title("🤖 Chatbot Scientifique Scopus")

query = st.text_input("Pose ta question (ex : deep learning en médecine)")

if query:
    # Encoder la question
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k=5)

    st.subheader("🧠 Résultats les plus pertinents :")
    for i in I[0]:
        article = articles[id_map[i]]
        st.markdown("### 📄 " + article.get("dc:title", "Titre inconnu"))
        st.markdown("**Résumé :** " + (article.get("dc:description", "Résumé indisponible") or "Résumé manquant"))
        st.markdown(f"**DOI :** {article.get('prism:doi', 'N/A')}")
        st.markdown(f"**Auteurs :** {article.get('dc:creator', 'Auteur inconnu')}")
        st.markdown(f"**Mots-clés :** {article.get('authkeywords', 'Non disponibles')}")
        st.markdown("---")
