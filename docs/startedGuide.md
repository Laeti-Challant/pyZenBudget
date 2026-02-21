# 💰 pyZenBudget - Documentation

Application Django de gestion de budget personnel avec import automatique de fichiers bancaires et catégorisation intelligente.

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
- **Application :** http://127.0.0.1:8000/

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

1. Aller sur http://127.0.0.1:8000/admin/budget/transaction/
2. Consulter les transactions importées
3. Filtrer par date, catégorie, etc.

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
│   ├── settings.py             # Paramètres
│   ├── urls.py                 # Routes principales
│   └── wsgi.py                 # Déploiement WSGI
│
├── budget/                      # Application principale
│   ├── __init__.py
│   ├── admin.py                # Interface d'administration
│   ├── apps.py                 # Configuration de l'application
│   ├── models.py               # Modèles de données
│   ├── tests.py                # Tests
│   ├── views.py                # Vues
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
    └── documentation.md
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

### ✅ Phase 2 : Import de données (TERMINÉ)

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

### 🚧 Phase 3 : Interface web (EN COURS)

- [ ] Page d'upload de fichiers
  - [ ] Formulaire d'upload Django
  - [ ] Prévisualisation du fichier
  - [ ] Configuration de la ligne de début
- [ ] Liste des transactions
  - [ ] Filtrage par date, catégorie, validation
  - [ ] Pagination
  - [ ] Recherche par libellé
- [ ] Interface de catégorisation
  - [ ] Validation manuelle des catégories
  - [ ] Interface "swipe" ou sélection rapide
  - [ ] Validation en batch
- [ ] Dashboard basique
  - [ ] Total par catégorie (mois en cours)
  - [ ] Évolution mensuelle
  - [ ] Indicateurs clés (dépenses/revenus)

### 📅 Phase 4 : Catégorisation intelligente (À VENIR)

- [ ] Système de règles automatiques
  - [ ] Création de règles depuis validation utilisateur
  - [ ] Moteur de matching (mots-clés, regex)
  - [ ] Priorisation des règles
- [ ] Apprentissage progressif
  - [ ] Détection de patterns récurrents
  - [ ] Suggestions de règles
  - [ ] Score de confiance évolutif
- [ ] Interface de gestion des règles
  - [ ] Liste des règles actives
  - [ ] Édition/suppression
  - [ ] Statistiques d'utilisation

### 📊 Phase 5 : Rapports et visualisation (À VENIR)

- [ ] Graphiques interactifs
  - [ ] Chart.js ou Plotly
  - [ ] Évolution par catégorie
  - [ ] Répartition des dépenses (camembert)
  - [ ] Tendances mensuelles/annuelles
- [ ] Exports
  - [ ] Export Excel des données catégorisées
  - [ ] Export PDF des rapports
  - [ ] Export CSV pour analyse externe
- [ ] Tableaux de bord avancés
  - [ ] Comparaison mois par mois
  - [ ] Budgets prévisionnels
  - [ ] Alertes de dépassement

### 🚀 Phase 6 : Fonctionnalités avancées (À VENIR)

- [ ] Gestion multi-comptes
- [ ] Gestion des devises
- [ ] Objectifs budgétaires
- [ ] Notifications/alertes
- [ ] API REST (pour app mobile future)
- [ ] Authentification utilisateurs multiples
- [ ] Thème sombre/clair

### 🌐 Phase 7 : Déploiement (À VENIR)

- [ ] Migration vers PostgreSQL (production)
- [ ] Configuration pour déploiement
- [ ] Déploiement sur Railway/Render
- [ ] Configuration du nom de domaine
- [ ] HTTPS/SSL
- [ ] Sauvegarde automatique des données

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

- **Ligne de début :** 9 (configurable avec `--start-row`)
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

**Version :** 0.2.0 (Phase 2 terminée, Phase 3 en cours)
