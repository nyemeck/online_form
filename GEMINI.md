# Projet : Formulaire de Recherche Académique (Université de Ngaoundéré)

## 📋 Contexte de Recherche
- **Chercheur :** Professeur Laurent BITJOKA (Master Professionnel en Management des Organisations Publiques, ISMP).
- **Mandat :** Étude scientifique sur la performance organisationnelle de l'Université de Ngaoundéré (UN), autorisée par le Recteur.
- **Thématique :** Innovation organisationnelle et managériale et performance de l'université.

## 🛠️ Architecture Technique
- **Backend :** Python (FastAPI), SQLite pour la base de données.
- **Frontend :** HTML/CSS/JS (Vanilla) pour un formulaire sobre et efficace.
- **Sécurité :** Authentification admin pour l'accès aux données et au tableau de bord.
- **Exports :** Génération de fichiers CSV/Excel pour analyse statistique.

## 📂 Structure du Projet
- **docs/** : Documents de référence (Mandat, Questionnaire PDF).
- **backend/** : Logique API, Modèles de données, Base de données.
- **frontend/** : Interface utilisateur (Formulaire, Dashboard, Login).
- **exports/** : Fichiers CSV/Excel générés pour analyse.

## 📝 Structure du Questionnaire (docs/Questionnaire 3.pdf)
- **Section A :** Informations générales (Sexe, Statut, etc.).
- **Sections B à F :** Échelles de Likert (1 à 5) sur l'innovation, la gouvernance, l'engagement et l'apprentissage.
- **Section G :** Mesure de la performance (Académique, Organisationnelle, Sociétale, Institutionnelle).
- **Final :** Remarque libre (optionnelle).

## ⚖️ Mandats de Données
- **Anonymat :** Les réponses doivent être strictement anonymes.
- **Intégrité :** Validation stricte des échelles de Likert (1-5 uniquement).
- **Disponibilité :** Les données doivent être exportables sans retraitement manuel.

## 🚀 État d'avancement
- [x] Analyse du mandat et du questionnaire.
- [x] Définition de l'architecture technique.
- [x] Création du fichier de contexte `GEMINI.md`.
- [ ] Initialisation du projet (Arborescence et dépendances).
- [ ] Développement du Backend (Modèles et API).
- [ ] Développement du Frontend (Formulaire et Dashboard).
