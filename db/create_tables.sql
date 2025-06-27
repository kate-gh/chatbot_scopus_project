CREATE DATABASE chatbot_scopus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chatbot_scopus;

-- Articles
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scopus_id VARCHAR(100) UNIQUE,
    titre TEXT,
    resume TEXT,
    date_publication VARCHAR(20),
    revue VARCHAR(255),
    doi VARCHAR(100),
    mots_cles TEXT,
    domaine_recherche TEXT
);

-- Auteurs
CREATE TABLE auteurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scopus_author_id VARCHAR(50) UNIQUE,
    nom_complet VARCHAR(255),
    orcid VARCHAR(100),
    affiliation_principale VARCHAR(255)
);

-- Affiliations
CREATE TABLE affiliations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_institution VARCHAR(255),
    pays VARCHAR(100),
    scopus_affiliation_id VARCHAR(50) UNIQUE
);

-- Relation article - auteur
CREATE TABLE article_auteur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT,
    auteur_id INT,
    FOREIGN KEY (article_id) REFERENCES articles(id),
    FOREIGN KEY (auteur_id) REFERENCES auteurs(id)
);

-- Relation auteur - affiliation
CREATE TABLE auteur_affiliation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    auteur_id INT,
    affiliation_id INT,
    FOREIGN KEY (auteur_id) REFERENCES auteurs(id),
    FOREIGN KEY (affiliation_id) REFERENCES affiliations(id)
);
