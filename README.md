# pyZenBudget

pyZenBudget est un projet personnel visant à apprendre Python et Django
à travers la création d’une application web de gestion de budget.

Le projet se concentre sur l’analyse de fichiers bancaires (Excel / CSV),
l’attribution de catégories et sous-catégories aux transactions,
et la visualisation des données budgétaires.

pyZenBudget est conçu comme une API REST autonome, pensée pour être consommée
par différents clients (un front web, une app mobile ou un script).
Le front est développé dans un dépôt séparé.

---

## 🎯 Objectifs du projet

- Apprendre Python dans un contexte d’application web
- Découvrir et pratiquer le framework Django
- Concevoir une API REST avec Django REST Framework
- Manipuler et analyser des données issues de fichiers bancaires
- Mettre en place une logique métier de gestion budgétaire

---

## 🧭 Contexte

Ce projet est développé progressivement, en parallèle d’une formation de Concepteur Développeur d’Applications.
Il est travaillé de manière itérative, environ toutes les deux semaines,
ce qui rend la documentation essentielle pour faciliter la reprise du projet.

Le projet a démarré en MVT pour explorer Django. En attaquant les vues,
j’ai constaté que la génération de templates ne me convenait pas.
J’ai donc décidé de le transformer en API REST, consommée par un front développé à part.
La logique métier (import, normalisation) reste inchangée, seule la couche de présentation évolue.

---

## 📦 Fonctionnalités envisagées

- Import de fichiers bancaires (CSV / Excel)
- Normalisation des données
- Attribution de catégories et sous-catégories
- Calcul et suivi du budget
- Visualisation des dépenses et des revenus

---

## 🛠️ Stack technique

- Python
- Django
- Django REST Framework (API)
- Pandas (pour le traitement des données)
- Base de données relationnelle (SQLite)

---

## 🧠 Ce que ce projet m’apporte

- Pratique de Python dans un contexte concret
- Compréhension de l’architecture d’une application Django
- Modélisation de données métier
- Structuration d’un projet long avec documentation

---

## 🚧 État du projet

Projet en cours de développement, évoluant progressivement
au rythme de l’apprentissage et des expérimentations.
