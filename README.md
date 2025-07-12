# Scopus AI – Chatbot académique intelligent

Un chatbot intelligent qui aide les utilisateurs à rechercher des articles scientifiques issus de la base de données **Scopus**, avec filtrage par année et auteur, historique des conversations, visualisations, et plus encore.

## Fonctionnalités principales

- Recherche d’articles scientifiques avec FAISS (similarité vectorielle)
- Filtres : par année de publication et par auteur
- Interface de chat moderne et responsive (Bootstrap 5)
- Historique des conversations avec horodatage
- Téléchargement des réponses et de l’historique complet en PDF
- Mode invité et utilisateur connecté
- Section « Mes Discussions » pour gérer les anciennes questions (voir/supprimer)
- Visualisations interactives (Plotly) :
  - Publications par auteur
  - Publications par domaine
  - Publications par pays

## Technologies utilisées

| Côté Serveur (Backend)                | Côté Client (Frontend)     |
| ------------------------------------- | -------------------------- |
| Python (Flask)                        | HTML5 / CSS3 / Bootstrap 5 |
| FAISS (Facebook AI Similarity Search) | JavaScript Vanilla         |
| MySQL (Base de données)               | Jinja2 Templates           |
| Plotly (Visualisations)               | FontAwesome Icons          |
| pdfkit + wkhtmltopdf (PDF)            | Responsive Design          |

---

## Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/kate-gh/chatbot_scopus_project.git
cd chatbot_scopus_project
```

### 2. Installer les dépendances Python

Assurez-vous d’avoir Python 3.8+ installé :

```bash
pip install -r requirements.txt
```

### 3. Configurer la base de données

- Créez une base de données MySQL `chatbot_scopus`
- Importez le fichier `create_tables.sql` pour créer les tables

### 4. Lancer le serveur Flask

```bash
python run.py
```

Le serveur est accessible sur : [http://localhost:5000/]

## Structure du projet

```
chatbot_scopus_project/
│
├── app/
│   ├── templates/
│   │   ├── index.html
│   │   ├── discussions.html
│   │   └── visualizations.html
│   ├── routes.py
│   ├── chatbot.py
│   ├── faiss_index.py
│   └── db.py
|── src/
│   ├── 1_extract_articles.py
│   ├── 2_parse_insert_mysql.py
│   ├── data_cleaning.py
├── run.py
├── requirements.txt
└── README.md
```

---

## Modes d’accès

- **Invité** : peut poser des questions, mais les discussions ne sont pas sauvegardées
- **Connecté** : peut consulter l’historique, gérer ses discussions, télécharger les résultats

---

## Contributeurs

- GANTOUH Kawtar
- LAGURIBI Omaima

---

## 📄 Licence

Projet réalisé dans le cadre du module Programmation Python Avancée – Master en Ingénierie Informatique et Analyse de Donnée(2IAD) – Université Chouaib DOUKKALI Faculté des Sciences.
