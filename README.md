# Guide utilisateur – Scopus AI – Chatbot académique intelligent

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

## Pré-requis

Avant de commencer, assurez-vous d’avoir installé :

- [Python 3.8+](https://www.python.org/downloads/)
- [XAMPP](https://www.apachefriends.org/index.html) ou [MySQL Server](https://dev.mysql.com/downloads/mysql/) + phpMyAdmin
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) (pour l’export PDF)
- Git (optionnel, pour cloner le dépôt)

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

Une fois lancé, l'application sera disponible à l’adresse :  
👉 http://localhost:5000/

Vous pouvez ensuite utiliser :

- Le mode **invité** sans inscription
- Le mode **connecté** en créant un compte

---

## Utilisation de l'application

1. Accédez à l’URL [http://localhost:5000](http://localhost:5000)
2. Dans l’interface de chat :
   - Posez une question en langage naturel (ex: _What are the latest articles in deep learning?_)
   - Utilisez les filtres (année, auteur)
3. Cliquez sur un résultat pour voir les détails :
   - **Résumé**, **DOI**, **auteurs**, **affiliations**
4. Enregistrez ou exportez :
   - Télécharger une réponse en PDF
   - Télécharger toute la conversation
5. Connectez-vous pour :
   - Accéder à l’historique ("Mes Discussions")
   - Supprimer ou revoir une ancienne question
6. Cliquez sur l’onglet **Visualisations** pour explorer :
   - Les publications par auteur, domaine ou pays sous forme de graphiques

---

## Structure du projet

```
chatbot_scopus_project/
│
├── app/
│   ├── templates/
|   |   ├── discussions.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── visualizations.html
│   ├── __init__.py
│   ├── auth.py
│   ├── routes.py
│   ├── chatbot.py
│   ├── faiss_index.py
│   └── db.py
|── src/
│   ├── 1_extract_articles.py
│   ├── 2_parse_insert_mysql.py
│   ├── data_cleaning.py
|── db/
│   ├── create_tables.sql
├── run.py
├── requirements.txt
└── README.md
```

## Modes d’accès

- **Invité** : peut poser des questions, mais les discussions ne sont pas sauvegardées
- **Connecté** : peut consulter l’historique, gérer ses discussions, télécharger les résultats

---

## Fonctionnement technique (en bref)

- Les questions sont vectorisées via **Sentence-BERT**
- La recherche sémantique est faite grâce à **FAISS**
- Les résultats sont extraits depuis une base locale d’articles Scopus (en JSON puis MySQL)
- Le tout est présenté via **Flask + HTML/CSS**
- L’export PDF utilise `pdfkit` et `wkhtmltopdf`

---

## Sécurité & Confidentialité

- Aucune donnée personnelle n’est partagée avec des services externes.
- L’historique de chaque utilisateur est stocké localement dans la base de données MySQL.

---

## Contributeurs

- GANTOUH Kawtar
- LAGURIBI Omaima

---

## 📄 Licence

Projet réalisé dans le cadre du module Programmation Python Avancée – Master en Ingénierie Informatique et Analyse de Donnée(2IAD) – Université Chouaib DOUKKALI Faculté des Sciences.
