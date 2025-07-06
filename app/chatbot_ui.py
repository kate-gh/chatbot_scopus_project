import streamlit as st
import json, faiss, numpy as np, mysql.connector, re
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime

# ========== CONFIGURATION DE LA PAGE ==========
st.set_page_config(
    page_title="Chatbot Scopus – Recherche Sémantique",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== INJECTION CSS ==========
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* Global */
    body { font-family: 'Segoe UI', sans-serif; }
    .stButton > button { background: linear-gradient(135deg,#10b981,#059669) !important; color:white !important; border-radius:8px; }
    .stButton > button:hover { box-shadow:0 4px 12px rgba(0,0,0,0.1) !important; }
    /* Header */
    .header-box { background: linear-gradient(90deg,#1e3a8a,#3b82f6); color:white; padding:2rem; border-radius:12px; text-align:center; margin-bottom:2rem; }
    /* Sidebar */
    .sidebar .stSelectbox, .sidebar .stSlider, .sidebar .stCheckbox { width:100%; }
    .sidebar-section { background:#f1f5f9; padding:1rem; border-radius:8px; margin-bottom:1rem; }
    /* Result Card */
    .result-card { background:white; border:1px solid #e5e7eb; border-left:4px solid #3b82f6; border-radius:8px; padding:1rem; margin-bottom:1rem; transition:box-shadow .2s; }
    .result-card:hover { box-shadow:0 4px 12px rgba(0,0,0,0.1); }
    .result-title { font-size:1.2rem; font-weight:600; color:#1e293b; margin-bottom:0.5rem; }
    .result-meta { font-size:0.9rem; color:#4b5563; margin-bottom:0.75rem; }
    .result-abstract { font-size:0.9rem; color:#374151; margin-bottom:0.75rem; }
    /* Links */
    .result-link { margin-right:1rem; color:#2563eb; text-decoration:none; font-size:0.9rem; }
    .result-link:hover { text-decoration:underline; }
    /* Footer */
    .footer { text-align:center; color:#6b7280; padding:1rem; border-top:1px solid #e5e7eb; margin-top:2rem; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# ========== UTILS ==========
def clean_html(txt: str) -> str:
    s = re.sub(r'<[^>]+>', '', str(txt))
    return re.sub(r'\s+', ' ', s).strip()

@st.cache_resource
def load_models_and_data():
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        index = faiss.read_index(str(Path(__file__).parent.parent / "data" / "semantic_index.faiss"))
        with open(Path(__file__).parent.parent / "data" / "id_map.json", encoding="utf-8") as f:
            id_map = json.load(f)
        with open(Path(__file__).parent.parent / "data" / "articles_clean.json", encoding="utf-8") as f:
            articles = json.load(f)
        # convert id_map dict -> list if needed
        if isinstance(id_map, dict):
            maxk = max(map(int, id_map.keys()))
            arr = [None]*(maxk+1)
            for k,v in id_map.items(): arr[int(k)] = v
            id_map = arr
        return model, index, id_map, articles
    except Exception as e:
        st.error(f"❌ Chargement des données impossible : {e}")
        return None, None, None, None

@st.cache_resource
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="chatbot_scopus", charset="utf8mb4"
        )
    except Exception as e:
        st.warning(f"⚠️ Base de données inacessible : {e}")
        return None

def semantic_search(query, model, index, id_map, articles, top_k=5):
    try:
        vec = model.encode([query], convert_to_numpy=True)
        D, I = index.search(np.array(vec), top_k)
        results = []
        for rank, (dist, idx0) in enumerate(zip(D[0], I[0]), start=1):
            if idx0 < len(id_map) and id_map[idx0] is not None:
                art = articles[id_map[idx0]]
                core = art.get("abstracts-retrieval-response", {}).get("coredata", {})
                res = {
                    "rank": rank,
                    "distance": float(dist),
                    "similarity": max(0,1-dist/2),
                    "title": clean_html(core.get("dc:title","")),
                    "abstract": clean_html(core.get("dc:description","")),
                    "journal": core.get("prism:publicationName",""),
                    "date": core.get("prism:coverDate",""),
                    "doi": core.get("prism:doi",""),
                    "scopus_id": core.get("dc:identifier","").replace("SCOPUS_ID:","")
                }
                results.append(res)
        return results
    except Exception as e:
        st.error(f"❌ Erreur recherche : {e}")
        return []

def get_database_stats(db):
    stats = {}
    if not db: return stats
    cur = db.cursor()
    for tbl in ["articles","auteurs","affiliations"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        stats[tbl] = cur.fetchone()[0]
    cur.close()
    return stats

# ========== MAIN ==========
def main():
    st.markdown('<div class="header-box"><h1>🔬 Chatbot Scopus</h1><p>Recherche sémantique avancée</p></div>', unsafe_allow_html=True)

    model, index, id_map, articles = load_models_and_data()
    db = get_db_connection()
    if not all([model, index, id_map, articles]):
        return

    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Statistiques")
        stats = get_database_stats(db)
        for k,v in stats.items(): st.write(f"**{k.capitalize()}**: {v}")
        st.markdown("---")
        st.markdown("## ⚙️ Paramètres")
        top_k = st.slider("Résultats max", 1, 20, 5)
        show_abs = st.checkbox("Afficher résumés", True)

    # Main search
    col1, col2 = st.columns([3,1])
    with col1:
        query = st.text_input("🔍 Votre requête scientifique", "")
        if st.button("Rechercher"):
            results = semantic_search(query, model, index, id_map, articles, top_k)
            st.markdown(f"### 📋 {len(results)} résultats pour « {query} »")
            for r in results:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="result-title">{r["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-meta">{r["journal"]} · {r["date"]} · Score: {r["similarity"]:.3f}</div>', unsafe_allow_html=True)
                if show_abs and r["abstract"]:
                    st.markdown(f'<div class="result-abstract">{r["abstract"]}</div>', unsafe_allow_html=True)
                links = ""
                if r["doi"]: links += f'<a class="result-link" href="https://doi.org/{r["doi"]}" target="_blank">DOI</a>'
                if r["scopus_id"]: links += f'<a class="result-link" href="https://www.scopus.com/record/display.uri?eid=2-s2.0-{r["scopus_id"]}" target="_blank">Scopus</a>'
                st.markdown(links, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sidebar-col">', unsafe_allow_html=True)
        st.markdown("### 💡 Guide")
        st.markdown("- Posez des questions en anglais\n- Utilisez mots-clés précis\n- Extraites les liens utiles")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="footer">Projet Master Python Avancée • Univ. Chouaïb Doukkali • {datetime.now().year}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
