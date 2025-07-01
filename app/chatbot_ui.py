# ✅ chatbot_ui.py — Interface professionnelle avec affichage corrigé des articles
import streamlit as st
import faiss
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ───── CONFIGURATION CSS PROFESSIONNELLE ──────────────────
st.set_page_config(
    page_title="Scopus Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement des icônes FontAwesome
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

# Style CSS personnalisé amélioré
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20"><defs><radialGradient id="a" cx="50%" cy="0%" r="100%"><stop offset="0%" stop-color="white" stop-opacity="0.1"/><stop offset="100%" stop-color="white" stop-opacity="0"/></radialGradient></defs><rect width="100" height="20" fill="url(%23a)"/></svg>');
    }
    
    .main-header h1 {
        position: relative;
        z-index: 1;
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .search-container {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid #e2e8f0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        position: relative;
    }
    
    .search-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px 20px 0 0;
    }
    
    .result-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 5px solid #667eea;
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
        border-left-color: #764ba2;
    }
    
    .article-title {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .article-meta {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    .meta-row {
        display: flex;
        align-items: center;
        margin-bottom: 0.8rem;
        padding: 0.3rem 0;
    }
    
    .meta-row:last-child {
        margin-bottom: 0;
    }
    
    .meta-icon {
        color: #667eea;
        width: 20px;
        margin-right: 12px;
        font-size: 0.9rem;
    }
    
    .meta-label {
        font-weight: 600;
        color: #374151;
        margin-right: 8px;
        min-width: 80px;
    }
    
    .meta-value {
        color: #1f2937;
        flex: 1;
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    .sidebar-section h3 {
        color: white;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-section p {
        position: relative;
        z-index: 1;
        margin: 0.5rem 0;
    }
    
    .sidebar-info {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .sidebar-info h3 {
        color: #1e293b;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    
    .status-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 5px solid #3b82f6;
        padding: 1.2rem 1.8rem;
        margin: 1rem 0;
        border-radius: 12px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
        color: #1e40af;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.2rem 1.8rem;
        margin: 1rem 0;
        border-radius: 12px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
        color: #92400e;
    }
    
    .results-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
    }
    
    .results-header h3 {
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        color: white;
    }
    
    .download-section {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
    }
    
    .download-section h3 {
        margin-top: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        color: white;
    }
    
    .download-section p {
        color: white;
        opacity: 0.9;
    }
    
    .doi-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .doi-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
        text-decoration: none;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3) !important;
        color: white !important;
    }
    
    .stButton > button:focus {
        color: white !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3) !important;
    }
    
    .footer {
        background: #f8fafc;
        color: #475569;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .footer h3 {
        color: #1e293b;
        margin-top: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
    }
    
    .sidebar-links a {
        color: #3b82f6;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .sidebar-links a:hover {
        background: #f1f5f9;
        transform: translateX(5px);
    }
    
    .summary-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-style: italic;
        color: #374151;
        line-height: 1.6;
    }
    
    /* Correction pour l'affichage du contenu HTML dans les résultats */
    .stExpander > div > div > div {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ───── PARAMÈTRES ───────────────────────────────────── 
base_dir = Path(__file__).resolve().parent.parent
articles_path = base_dir / "data" / "articles_clean.json"
id_map_path = base_dir / "data" / "id_map.json"
faiss_index_path = base_dir / "data" / "semantic_index.faiss"

# ───── FONCTIONS UTILITAIRES ─────────────────────────
def safe_get(data, key, default="Non spécifié"):
    """Récupération sécurisée des données avec valeur par défaut"""
    value = data.get(key, default)
    if not value or str(value).strip() == "":
        return default
    return str(value).strip()

def format_authors(authors):
    """Formatage des auteurs"""
    if isinstance(authors, list):
        if len(authors) > 3:
            return ", ".join(authors[:3]) + f" et {len(authors)-3} autres"
        return ", ".join(authors)
    return str(authors) if authors else "Auteur inconnu"

def truncate_text(text, max_length=150):
    """Troncature du texte avec ellipses"""
    if len(str(text)) > max_length:
        return str(text)[:max_length] + "..."
    return str(text)

def clean_html_content(content):
    """Nettoie le contenu HTML pour affichage propre"""
    import re
    # Supprime les balises HTML
    content = re.sub(r'<[^>]+>', '', str(content))
    # Nettoie les espaces multiples
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

# ───── VÉRIFICATION ET CHARGEMENT SÉCURISÉ DES DONNÉES ─────── 
@st.cache_data
def load_data():
    try:
        # Vérification de l'existence des fichiers
        if not articles_path.exists():
            st.error(f"❌ Fichier articles non trouvé: {articles_path}")
            return None, None, None
        
        if not id_map_path.exists():
            st.error(f"❌ Fichier id_map non trouvé: {id_map_path}")
            return None, None, None
            
        if not faiss_index_path.exists():
            st.error(f"❌ Index FAISS non trouvé: {faiss_index_path}")
            return None, None, None
        
        # Chargement des données
        with open(articles_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        
        with open(id_map_path, "r", encoding="utf-8") as f:
            id_map = json.load(f)
        
        # Conversion de id_map si nécessaire
        if isinstance(id_map, dict):
            max_index = max(map(int, id_map.keys()))
            id_map_list = [None] * (max_index + 1)
            for k, v in id_map.items():
                id_map_list[int(k)] = v
            id_map = id_map_list
            
        index = faiss.read_index(str(faiss_index_path))
        
        return articles, id_map, index
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        return None, None, None

@st.cache_resource
def load_model():
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du modèle: {str(e)}")
        return None

# Chargement des données
articles, id_map, index = load_data()
model = load_model()

# Vérification que tout est chargé correctement
if articles is None or id_map is None or index is None or model is None:
    st.stop()

# ───── EN-TÊTE PRINCIPAL ─────────────────────────────
st.markdown("""
<div class="main-header">
    <h1><i class="fas fa-microscope"></i> Scopus Research Assistant</h1>
    <p style="font-size: 1.2rem; opacity: 0.9; position: relative; z-index: 1;">Intelligence Artificielle pour la Recherche Scientifique</p>
    <p style="font-size: 1rem; opacity: 0.8; position: relative; z-index: 1;">Projet Master Python Avancée - Université Chouaïb Doukkali</p>
</div>
""", unsafe_allow_html=True)

# ───── SIDEBAR PROFESSIONNELLE ──────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-section">
        <h3><i class="fas fa-database"></i> Base de Données</h3>
        <p><strong>Source:</strong> Scopus</p>
        <p><strong>Articles indexés:</strong> {len(articles):,}</p>
        <p><strong>Modèle IA:</strong> MiniLM-L6-v2</p>
        <p><strong>Moteur:</strong> FAISS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-info">
        <h3><i class="fas fa-bullseye"></i> Guide d'utilisation</h3>
        <ul style="padding-left: 1.2rem;">
            <li>Rédigez vos questions en anglais</li>
            <li>Utilisez des termes scientifiques précis</li>
            <li>Filtrez par année si nécessaire</li>
            <li>Exportez vos résultats en CSV</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-info">
        <h3><i class="fas fa-link"></i> Ressources</h3>
        <div class="sidebar-links">
            <a href="https://www.scopus.com" target="_blank"><i class="fas fa-book"></i> Base Scopus</a>
            <a href="https://github.com" target="_blank"><i class="fab fa-github"></i> Code Source</a>
            <a href="https://www.elsevier.com" target="_blank"><i class="fas fa-building"></i> Elsevier</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ───── INTERFACE DE RECHERCHE ───────────────────────
st.markdown('<div class="search-container">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "🔍 Recherche sémantique avancée",
        placeholder="Ex: machine learning applications in healthcare, deep learning in cancer detection...",
        help="Formulez votre requête en anglais pour des résultats optimaux"
    )

with col2:
    # Extraction sécurisée des années
    try:
        annees = sorted({
            a.get("prism:coverDate", "")[:4] 
            for a in articles 
            if a.get("prism:coverDate") and len(a.get("prism:coverDate", "")) >= 4
        })
        annees = [a for a in annees if a.isdigit()]  # Filtrer les années valides
    except Exception:
        annees = []
    
    annee_select = st.selectbox(
        "📅 Filtrer par année", 
        ["Toutes"] + annees
    )

st.markdown('</div>', unsafe_allow_html=True)

# ───── TRAITEMENT DE LA REQUÊTE ─────────────────────── 
if query:
    st.markdown("""
    <div class="status-info">
        <i class="fas fa-cog fa-spin"></i> <strong>Analyse sémantique en cours...</strong><br>
        Recherche des articles les plus pertinents dans la base Scopus
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Encodage de la requête
        query_vec = model.encode([query])
        D, I = index.search(np.array(query_vec), k=5)

        st.markdown("## 📊 Résultats de la recherche", unsafe_allow_html=False)
        
        # Récupération sécurisée des résultats
        results = []
        for i in I[0]:
            if i < len(id_map) and id_map[i] is not None and id_map[i] < len(articles):
                results.append(articles[id_map[i]])

        # Filtrage par année si nécessaire
        if annee_select != "Toutes":
            results = [
                a for a in results 
                if a.get("prism:coverDate", "").startswith(annee_select)
            ]

        if not results:
            st.markdown("""
            <div class="status-warning">
                <i class="fas fa-exclamation-triangle"></i> <strong>Aucun résultat trouvé</strong><br>
                Essayez de reformuler votre requête ou modifiez les filtres de recherche.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Affichage du nombre de résultats
            st.markdown(f"""
            <div class="results-header">
                <h3><i class="fas fa-list"></i> {len(results)} article(s) trouvé(s)</h3>
            </div>
            """, unsafe_allow_html=True)

            # Affichage des résultats
            for idx, article in enumerate(results, 1):
                # Récupération et formatage sécurisé des données
                titre = safe_get(article, "dc:title", "Titre non disponible")
                resume = safe_get(article, "dc:description", "Résumé non disponible")
                mots_cles = safe_get(article, "authkeywords", "Non spécifiés")
                date_pub = safe_get(article, "prism:coverDate", "Date inconnue")
                auteurs = format_authors(article.get("dc:creator", "Auteur inconnu"))
                doi = article.get("prism:doi")
                revue = safe_get(article, "prism:publicationName", "Revue inconnue")
                
                # Nettoyage du contenu HTML
                titre_clean = clean_html_content(titre)
                resume_clean = clean_html_content(resume)
                
                # Troncature du titre si trop long
                titre_display = truncate_text(titre_clean, 120)
                auteurs_display = truncate_text(auteurs, 100)
                revue_display = truncate_text(revue, 80)

                # Carte d'article avec design professionnel
                st.markdown(f"""
                <div class="result-card">
                    <div class="article-title">
                        📄 {titre_display}
                    </div>
                    
                    <div class="article-meta">
                        <div class="meta-row">
                            <i class="fas fa-calendar-alt meta-icon"></i>
                            <span class="meta-label">Date:</span>
                            <span class="meta-value">{date_pub}</span>
                        </div>
                        <div class="meta-row">
                            <i class="fas fa-user-edit meta-icon"></i>
                            <span class="meta-label">Auteur(s):</span>
                            <span class="meta-value">{auteurs_display}</span>
                        </div>
                        <div class="meta-row">
                            <i class="fas fa-journal-whills meta-icon"></i>
                            <span class="meta-label">Revue:</span>
                            <span class="meta-value">{revue_display}</span>
                        </div>
                        <div class="meta-row">
                            <i class="fas fa-tags meta-icon"></i>
                            <span class="meta-label">Mots-clés:</span>
                            <span class="meta-value">{truncate_text(mots_cles, 100)}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Lien DOI
                if doi:
                    lien = f"https://doi.org/{doi}"
                    st.markdown(f"""
                    <a href="{lien}" target="_blank" class="doi-button">
                        <i class="fas fa-external-link-alt"></i> Consulter l'article
                    </a>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

                # Résumé dans un expander - CORRIGÉ
                with st.expander(f"📖 Lire le résumé complet - Article {idx}"):
                    # On affiche directement le texte nettoyé sans HTML
                    st.write(resume_clean)
                
                st.markdown("---")

            # Section téléchargement
            st.markdown("""
            <div class="download-section">
                <h3><i class="fas fa-download"></i> Exporter les résultats</h3>
                <p>Téléchargez tous les résultats au format CSV pour analyse ultérieure</p>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                df = pd.DataFrame(results)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Télécharger les résultats en CSV", 
                    csv, 
                    f"scopus_recherche_{query.replace(' ', '_')[:50]}.csv", 
                    "text/csv",
                    help="Exporte tous les articles trouvés au format CSV"
                )
            except Exception as e:
                st.error(f"❌ Erreur lors de l'export: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche: {str(e)}")

# ───── FOOTER ─────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3><i class="fas fa-graduation-cap"></i> Projet Master Python Avancée</h3>
    <p><strong>Université Chouaïb Doukkali - Faculté des Sciences</strong></p>
    <p style="margin-bottom: 0; opacity: 0.8;">
        Développé avec <i class="fas fa-heart" style="color: #e11d48;"></i> • Streamlit • FAISS • Sentence Transformers • Scopus API
    </p>
</div>
""", unsafe_allow_html=True)