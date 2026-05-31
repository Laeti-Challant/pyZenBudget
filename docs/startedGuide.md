# 💰 pyZenBudget - Guide de suivi

API Django (REST Framework) de gestion de budget personnel, avec import de fichiers bancaires
et catégorisation intelligente. Le front est développé dans un dépôt séparé.
Ce document me sert de carnet de suivi : comme j'avance par intermittence,
il me permet de me replonger vite dans le projet.

---

## 🧭 Journal de bord

### Mai 2026 : passage de MVT à une API

Le projet a démarré en MVT pour explorer Django. En attaquant les vues,
j'ai constaté que la génération de templates ne me convenait pas.
Décision : transformer le projet en API REST autonome, consommée par un front React
développé dans un dépôt séparé.
La logique métier (import, normalisation) évolue également. Je vais mettre en place les analyses des entrées (totaux par catégorie et par période). Puis le budget avec donc un nouveau modèle et une migration. Viendront ensuite les règles de catégorisation et l'apprentissage.
Les endpoints API ne viendront qu'une fois l'application fonctionnelle à un niveau personnel.

Généralisation de la normalisation avec ajout de variable.
La commande d'import reste un outil de dev, le mapping configurable par l'utilisateur passera par l'API.

---

## 🚀 Guide de démarrage rapide

### Prérequis

- Python 3.12+
- SQLite pour le développement
- Git

---

## 🔧 Démarrage du projet

### 1. Cloner le projet (si nécessaire)

```bash
cd ~/projets
git clone https://github.com/ton-username/pyzenbudget.git
cd pyzenbudget
```

### 2. Activer l'environnement virtuel

#### Sur Linux/Mac (Pop!\_OS)

```bash
# Activer l'environnement existant
source venv/bin/activate

# (venv) apparaîs dans le terminal
# (venv) user@machine:~/pyzenbudget$
```

#### Sur Windows

```bash
venv\Scripts\activate
```

#### Si l'environnement n'existe pas

```bash
# Créer un nouvel environnement virtuel
python3 -m venv venv

# Puis l'activer
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Vérifier les dépendances

```bash
# Voir ce qui est installé
pip list

# Installer/mettre à jour si nécessaire
pip install -r requirements.txt
```

### 4. Lancer le serveur Django

```bash
# Appliquer les migrations (si besoin)
python manage.py migrate

# Lancer le serveur de développement
python manage.py runserver

# Le serveur démarre sur http://127.0.0.1:8000/
```

### 5. Accéder à l'application

- **Interface admin :** http://127.0.0.1:8000/admin/
- API (racine) : http://127.0.0.1:8000/api/
- API navigable DRF : http://127.0.0.1:8000/api/ (interface fournie par DRF pour tester les endpoints)

---

## 📦 Import de fichiers bancaires

### Via commande Django (méthode recommandée)

```bash
# Import simple
python manage.py import_bank_file data/raw/export_janvier.xlsx

# Avec ligne de début personnalisée
python manage.py import_bank_file data/raw/export.xlsx --start-row 7
```

### Via l'interface admin

L'admin Django sert à consulter et corriger les transactions (filtrer par date,
catégorie, validation) et à en ajouter une manuellement. Par défaut, il ne permet pas
d'importer un fichier bancaire.

1. Aller sur http://127.0.0.1:8000/admin/budget/transaction/
2. Consulter les transactions importées, filtrer, corriger
3. Ajouter une transaction manuellement si besoin

### Via le bouton d'import dans l'admin (à ajouter)

Un bouton « Importer un fichier bancaire » sur la page des transactions, pour importer
sans passer par le terminal. Il ouvre un formulaire (fichier + ligne de début) qui réutilise
la même logique d'import que la commande.

> Note : ce bouton est un confort côté admin, pour mon usage. L'import destiné aux clients
> de l'API (front, script, etc.) passera par un endpoint dédié, voir Phase 4.

---

## 🗂️ Structure du projet

```
pyZenBudget/
├── manage.py                    # Point d'entrée Django
├── requirements.txt             # Dépendances Python
├── README.md                    # Documentation principale
├── db.sqlite3                   # Base de données (dev)
│
├── config/                      # Configuration Django
│   ├── __init__.py
│   ├── asgi.py                 # Déploiement ASGI
│   ├── settings.py             # Paramètres (+ rest_framework, corsheaders)
│   ├── urls.py                 # Routes principales (inclut les routes API)
│   └── wsgi.py                 # Déploiement WSGI
│
├── budget/                      # Application principale
│   ├── __init__.py
│   ├── admin.py                # Interface d'administration
│   ├── apps.py                 # Configuration de l'application
│   ├── models.py               # Modèles de données
│   ├── serializers.py          # À VENIR : sérialisation des modèles pour l'API
│   ├── views.py                # ViewSets DRF (remplacent les vues MVT)
│   ├── urls.py                 # À VENIR : router DRF de l'application
│   ├── tests.py                # Tests
│   │
│   ├── importers/              # Logique d'import
│   │   ├── __init__.py
│   │   ├── excel_normalizer.py    # Normalise Excel → format standard
│   │   └── excel_importer.py      # Import en base de données
│   │
│   ├── management/             # Commandes Django
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── import_bank_file.py    # Commande d'import
│   │       └── seed_categories.py     # Créer catégories de base
│   │
│   └── migrations/             # Migrations de base de données
│       ├── __init__.py
│       └── 0001_initial.py
│
├── data/                        # Données (gitignore)
│   ├── raw/                    # Fichiers bancaires bruts
│   └── processed/              # Fichiers normalisés
│
└── docs/                        # Documentation
    └── startedGuide.md          # Ce guide de suivi
```

---

## 📊 Modèles de données

### Category

- Catégories de dépenses/revenus (Alimentation, Transport, Salaire...)
- Hiérarchie possible (parent/enfant)
- Couleur pour graphiques

### Transaction

- Opérations bancaires importées
- Date, libellé, montant
- Lien vers catégorie
- Statut de validation utilisateur
- **Gestion des doublons via compteur d'occurrence**

### CategorizationRule

- Règles de catégorisation automatique
- Pattern (mot-clé) → Catégorie
- Score de confiance
- Compteur d'utilisation

### ImportProfile (prévu, Phase 4)

- Mémorise un mapping de colonnes (ligne d'en-tête + correspondances)
- Permet de réutiliser une configuration pour les exports récurrents d'une même banque

---

## 🛠️ Commandes utiles

### Django

```bash
# Créer les tables
python manage.py migrate

# Créer un super-utilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Accéder au shell Django
python manage.py shell

# Créer les catégories de base
python manage.py seed_categories
```

### Git

```bash
# Voir l'état
git status

# Ajouter des fichiers
git add .

# Commit
git commit -m "feat: description de la fonctionnalité"

# Push
git push origin main

# Voir l'historique
git log --oneline
```

### Environnement virtuel

```bash
# Activer
source venv/bin/activate

# Désactiver
deactivate

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```

---

## 🗺️ Roadmap du projet

### ✅ Phase 1 : Fondations (TERMINÉ)

- [x] Structure Django de base
- [x] Modèles de données (Category, Transaction, CategorizationRule)
- [x] Interface d'administration Django
- [x] Base de données SQLite configurée
- [x] Système de migrations

### ✅ Phase 2 : Import de données (Terminé)

- [x] Normalisation de fichiers Excel
  - [x] Lecture avec ligne de début configurable
  - [x] Gestion Débit/Crédit → Montant unique
  - [x] Format de date standardisé (ISO 8601)
- [x] Import en base de données
  - [x] Détection de doublons avec compteur d'occurrence
  - [x] Vérification des colonnes requises
  - [x] Gestion des erreurs
- [x] Commande Django `import_bank_file`
- [x] Catégories de base créées
- [x] **Normaliseur paramétrable **
  - [x] Le normaliseur reçoit un mapping (ligne d'en-tête + correspondance des colonnes)
        au lieu de valeurs codées en dur
  - [x] Mise à jour de `import_bank_file` pour ajouter les options de mapping
  - [x] Test via `import_bank_file` avec un fichier bancaire

### 🚧 Phase 3 : Logique métier (À VENIR)

- [ ] Mettre en place les calculs de totaux sur des périodes et selon des catégories
- [ ] **Mise en place des budgets**
  - [ ] mise en place de la table
  - [ ] migration
- [ ] Complétion des categorisation_rules
- [ ] **Mise en place de l'auto-apprentissage des categorisation_rules**
  - [ ] Moteur qui applique les CategorizationRule à l'import
  - [ ] Score de confiance
  - [ ] Tri de la liste : transactions non catégorisées ou peu sûres renvoyées en tête
  - [ ] Apprentissage : création/mise à jour d'une règle à chaque correction de l'utilisateur

### 📅 Phase 4 : Interface web (À VENIR)

> 📌 Remplace l'interface web en MVT initialement prévue (voir Journal de bord).
> Les écrans (upload, liste, validation, dashboard) sont désormais dans le dépôt du front.

- [ ] Installer et configurer Django REST Framework
- [ ] Serializers des modèles (Category, Transaction, CategorizationRule)
- [ ] ViewSets en lecture seule + router
- [ ] Configurer CORS (django-cors-headers) pour autoriser les clients web
- [ ] Tester dans l'API navigable et Postman
- [ ] (Authentification différée : mono-utilisateur pour l'instant, voir Phase 8)

### 📅 Phase 5 : Import flexible (endpoints) (À VENIR)

Expose le normaliseur paramétrable (Phase 2) via l'API, pour que n'importe quel client
puisse importer un fichier en définissant son mapping.

- [ ] Endpoint d'upload qui renvoie un aperçu (lignes brutes + colonnes détectées)
- [ ] Endpoint d'import qui applique le mapping fourni par le client
- [ ] Modèle `ImportProfile` pour mémoriser et réutiliser un mapping (banque récurrente)

### 📅 Phase 6 : Catégories et sous-catégories (endpoints) (À VENIR)

- [ ] Endpoints CRUD des catégories (hiérarchie parent/enfant)
- [ ] Endpoint d'affectation d'une catégorie à une transaction (PATCH)
- [ ] Liste des transactions : filtrage (date, catégorie, validation), pagination, recherche par libellé

### 📊 Phase 7 : Rapports et exports (endpoints) (À VENIR)

- [ ] Endpoints d'agrégation (JSON consommé par le front pour les graphiques)
  - [ ] Total par catégorie (mois en cours)
  - [ ] Évolution mensuelle
  - [ ] Indicateurs clés (dépenses/revenus)
- [ ] Exports
  - [ ] Export Excel des données catégorisées
  - [ ] Export CSV pour analyse externe
  - [ ] Export PDF des rapports

### 🚀 Phase 8 : Avancé et déploiement (À VENIR)

- [ ] Documentation de l'API : schéma OpenAPI + Swagger (drf-spectacular), le contrat que les clients consultent
- [ ] Authentification (JWT, multi-utilisateurs)
- [ ] Gestion multi-comptes et devises
- [ ] Notifications de dépassement de budget
- [ ] Migration vers PostgreSQL (production)
- [ ] Déploiement (Railway/Render), nom de domaine, HTTPS/SSL, sauvegardes

---

## 🐛 Résolution de problèmes

### Le serveur ne démarre pas

```bash
# Vérifier que l'environnement virtuel est activé
which python
# Doit afficher : /chemin/vers/pyzenbudget/venv/bin/python

# Vérifier les migrations
python manage.py migrate

# Vérifier les erreurs
python manage.py check
```

### Import de fichier échoue

```bash
# Vérifier les colonnes du fichier
python -c "
from budget.importers.excel_normalizer import ExcelNormalizer
n = ExcelNormalizer('data/raw/fichier.xlsx', start_row=9)
n.read_file()
print('Colonnes:', list(n.df.columns))
"

# Adapter les noms de colonnes dans budget/importers/excel_normalizer.py
# Lignes à vérifier : 43, 51, 52, 57
```

### Base de données verrouillée (SQLite)

```bash
# Arrêter le serveur Django (Ctrl+C)
# Puis relancer
python manage.py runserver
```

### Mot de passe admin oublié

```bash
python manage.py changepassword ton_username
```

---

## 📝 Notes de développement

### Format des fichiers Excel attendu

> Avec le normaliseur paramétrable (Phase 2) et l'API (Phase 4), ces valeurs deviennent
> configurables par le client. En attendant, l'import par commande suppose ce qui suit.

- **Ligne de début :** 10 (configurable avec `--start-row`)
- **Colonnes requises après normalisation :**
  - `Date` : Format français DD/MM/YYYY
  - `Libellé` : Description de la transaction
  - `Débit euros` : Montant débité
  - `Crédit euros` : Montant crédité

### Format standardisé (après normalisation)

- `Date` : YYYY-MM-DD (ISO 8601)
- `Label` : Libellé de la transaction
- `Amount` : Montant signé (négatif = dépense, positif = revenu)

### Gestion des doublons

- Utilise un **compteur d'occurrence** pour accepter les vraies transactions identiques
- Détecte les réimports via comparaison date+libellé+montant

### CORS (API et clients sur des origines différentes)

L'API et les clients web tournent sur des origines différentes (ports distincts en dev).
Il faut donc installer et configurer `django-cors-headers` côté Django :

```bash
pip install django-cors-headers
```

Puis autoriser l'origine du client dans les settings (en développement uniquement).

---

## 🔐 Sécurité

### Fichiers à ne JAMAIS committer

```
db.sqlite3
*.sqlite3
data/raw/*
data/processed/*
venv/
.env
```

### Variables sensibles

Utiliser un fichier `.env` pour :

- Clé secrète Django (`SECRET_KEY`)
- Identifiants base de données
- Configuration email (future)

---

## 📚 Ressources

### Documentation

- [Django Official Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python DateUtil](https://dateutil.readthedocs.io/)

### Stack technique

- **Backend :** Python 3.12, Django 6.0
- **Base de données :** SQLite (dev), PostgreSQL (prod prévu)
- **Traitement de données :** Pandas, OpenPyXL
- **Tests :** pytest, pytest-django (à ajouter)

---

## 🤝 Contribution

### Convention de commits

```bash
feat: nouvelle fonctionnalité
fix: correction de bug
docs: documentation
style: formatage, points-virgules manquants, etc.
refactor: refactorisation du code
test: ajout de tests
chore: maintenance, mise à jour de dépendances
```

### Workflow Git

```bash
# Créer une branche pour une nouvelle fonctionnalité
git checkout -b feature/nom-fonctionnalite

# Développer, tester, commiter

# Pousser la branche
git push origin feature/nom-fonctionnalite

# Merger dans main une fois validé
git checkout main
git merge feature/nom-fonctionnalite
```

---

## 📞 Support

### En cas de blocage

1. Vérifier cette documentation
2. Consulter les logs d'erreur Django
3. Vérifier l'état Git : `git status`
4. Consulter l'historique de commits : `git log`

---

**Dernière mise à jour :** {{ date }}

**Version :** 0.3.0 (Phase 2 en finalisation, passage en API REST en cours)
