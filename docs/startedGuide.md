# 💰 pyZenBudget - Guide de suivi

API Django (REST Framework) de gestion de budget personnel, avec import de fichiers bancaires
et catégorisation intelligente. Le front est développé dans un dépôt séparé.
Ce document me sert de carnet de suivi : comme j'avance par intermittence,
il me permet de me replonger vite dans le projet.

---

## 🧭 Journal de bord

### 28 juillet 2026 : Phase 1 du cadrage front, liste définitive des écrans

Suite directe de la session du 26 juillet : à partir de l'inventaire fonctionnel déjà
posé, discussion écran par écran pour arriver à une liste définitive, avant les
maquettes basse fidélité.

**Écrans actés (4, au lieu des 6 pressentis au départ, grâce à deux fusions) :**
- **Dashboard** : section annuelle + onglets mensuels, filtre par catégorie intégré.
  La comparaison à date équivalente est écartée du v1 (jugée trop lourde à intégrer
  avant d'avoir vécu avec les onglets mensuels), notée pour réévaluation après usage
  réel, dans le même esprit que la Phase 6 réactivée seulement une fois le besoin
  confirmé en pratique
- **Transactions** : liste paginée, filtres catégorie/montant/mois, catégorisation
  manuelle via une fenêtre modale (plutôt qu'en édition directe dans le tableau, pour
  éviter les recatégorisations accidentelles par mis-clic)
- **Import/Révision** : fusion actée. Clic Import depuis le Dashboard -> formulaire
  d'upload -> une fois le fichier lu, redirection automatique vers la page de
  Révision (transactions à faible confiance issues de cet import). Cette page reste
  aussi accessible en permanence (menu ou lien Dashboard), pour une révision
  ponctuelle indépendante d'un import, car `review` regarde toute la base et pas
  seulement le dernier import
- **Catégories** : fusion avec Budgets actée. Arborescence dépliable (catégorie
  parente + sous-catégories dessous, jugée plus visuelle qu'une liste à plat avec
  colonne "Parent"), indicateur "charge fixe" par ligne, CRUD catégories. Budgets
  accrochés au même écran (CRUD, seuil d'alerte), car un budget est toujours rattaché
  à une catégorie

**Idée remontée pour la Phase 6 (implémentation API, pas encore tranchée) :** traiter
une recatégorisation manuelle depuis l'écran Transactions comme un rejet implicite de
la règle de catégorisation automatique appliquée (baisse de `confidence`), plutôt que
comme une simple réaffectation neutre. À trancher au moment de construire l'endpoint
`PATCH` d'affectation de catégorie.

Prochaine étape : maquettes basse fidélité (Figma, méthode déjà validée : formes
natives + composants perso, pas de kit UI externe).

### 26 juillet 2026 : cadrage fonctionnel du front, avant tout développement

Session de conception (pas de code), pour lister les fonctionnalités voulues avant de
se lancer dans les maquettes et le développement Next.js, plutôt que de repartir "à
l'envers" comme au début du projet (voir Mai 2026 ci-dessous).

**Fonctionnalités déjà couvertes par l'API existante (travail front seul) :**
- Agrégations par catégorie (`summary`, `monthly`, `yearly`)
- Dashboard annuel avec zoom mois/catégorie (`yearly` contient déjà le détail)
- Recherche par catégorie (paramètre `category` sur la liste des transactions)
- Comparaison à date équivalente (deux appels `summary` avec des plages différentes, calcul front)
- Validation des catégorisations automatiques (`review`, `matches`, `categorize` fonctionnels, il ne manque que l'écran)

**Nouveau périmètre API identifié :**
- Pagination de la liste des transactions (`DRF PageNumberPagination`, `list()` est actuellement écrit à la main)
- Endpoint `POST` d'upload de fichier bancaire pour le front, format fixe uniquement (pas de mapping flexible, voir Phase 5)
- CRUD Catégorie, avec choix d'un `parent` à la création (aucun endpoint n'existe aujourd'hui)
- CRUD Budget (aucun endpoint n'existe aujourd'hui)
- Filtre par montant (min/max) sur la liste des transactions
- Paramètre `month=YYYY-MM` direct sur la liste des transactions (cohérent avec `monthly`/`yearly`)
- Champ "seuil d'alerte" (stocké côté API, partagé) probablement sur `Budget`
- Champ booléen "charge fixe" sur `Category` (utilisable au niveau sous-catégorie), pour distinguer les charges qui reviennent tous les mois (loyer, assurances) du reste

**Mis de côté volontairement, pas dans ce périmètre :**
- Détection automatique de récurrence (couverte par l'apprentissage des règles de catégorisation existant)
- Transactions "hors budget" (dépenses exceptionnelles à exclure du bilan) : trop tôt, à reconsidérer après usage réel

**Décisions actées :**
- Import : reste un format fixe unique (les fichiers bancaires de Laetitia sont déjà réglés), pas d'import flexible multi-mapping. Juste exposé via un endpoint `POST` en plus de la commande CLI existante
- Seuils d'alerte de budget : stockés côté API (partagés entre elle et son compagnon, standard si portage Java plus tard). La traduction en couleur/alerte visuelle reste côté front (logique de présentation, décision antérieure inchangée)
- Charges fixes : indicateur posé sur la (sous-)catégorie, pas sur chaque transaction. Pas d'héritage automatique parent → enfant (une sous-catégorie comme "Assurance emprunteur" est marquée individuellement)
- **Sous-catégories réactivées dans le scope actuel**, plus tôt que prévu par la Phase 6 (initialement reportée "après un usage réel du front"). Déclenché par la réflexion sur les charges fixes : une catégorisation grossière ("Logement") ne suffit pas à isoler les charges fixes (emprunt, assurance emprunteur, assurance maison)
- Filtre mensuel sur la liste des transactions : paramètre `month=` direct plutôt que de faire calculer `start`/`end` au front

Prochaine étape : Phase 1 de la conception (liste définitive des écrans du front), maquettes basse fidélité, puis développement du dépôt Next.js.

### Juillet 2026 : fin de la Phase 3 (logique métier)

Endpoints `summary`, `monthly` et `yearly` ajoutés pour les totaux par période/catégorie,
avec les budgets mensuels en base (table + migration).

Complétion des `categorisation_rules` : `rejected_count` ajouté au modèle en plus de
`usage_count`, pour calculer un score de confiance (`usage_count / (usage_count + rejected_count)`,
recalculé seulement à partir du premier événement pour éviter la division par zéro).

Deux endpoints pour le flux de validation manuelle : `matches` (cherche les transactions
non catégorisées correspondant à un pattern) et `categorize` (soumet les transactions
validées/rejetées, met à jour la règle en conséquence).

Auto-apprentissage : `CategorizationRule.best_match(label)` cherche la meilleure règle
correspondante (tie-break par confiance puis usage), branché dans `excel_importer.py`
pour catégoriser automatiquement à l'import (sans valider, `applied_rule` trace quelle
règle a été utilisée). Endpoint `review` ajouté pour lister ce qui reste à vérifier
(non catégorisé, ou catégorisé avec une confiance sous `LOW_CONFIDENCE_THRESHOLD`).

Décision actée : l'authentification multi-utilisateurs reste reportée à la Phase 8,
comme prévu initialement (aucun modèle n'a de FK `user` pour l'instant).

Phase 3 terminée. Prochaine étape : l'interface (Phase 4), dans le dépôt front séparé.

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
- Lien vers la `CategorizationRule` qui l'a catégorisée automatiquement (`applied_rule`, traçabilité)

### CategorizationRule

- Règles de catégorisation automatique
- Pattern (mot-clé) → Catégorie
- Score de confiance (recalculé à chaque validation/rejet, tant qu'au moins un des deux a eu lieu)
- Compteur d'utilisation (validations) et compteur de rejets
- `best_match(label)` : trouve la règle la plus fiable dont le pattern est contenu dans un libellé donné (insensible à la casse), utilisée à l'import

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

### ✅ Phase 3 : Logique métier (Terminé)

- [x] Mettre en place les calculs de totaux sur des périodes et selon des catégories
- [x] **Mise en place des budgets**
  - [x] mise en place de la table
  - [x] migration
- [x] Complétion des categorisation_rules
- [x] **Mise en place de l'auto-apprentissage des categorisation_rules**
  - [x] Moteur qui applique les CategorizationRule à l'import
  - [x] Score de confiance
  - [x] Tri de la liste : transactions non catégorisées ou peu sûres renvoyées en tête
  - [x] Apprentissage : création/mise à jour d'une règle à chaque correction de l'utilisateur

### 🚧 Phase 4 : Interface web (En cours)

> 📌 Remplace l'interface web en MVT initialement prévue (voir Journal de bord).
> Les écrans (upload, liste, validation, dashboard) sont désormais dans le dépôt du front.

- [x] Installer et configurer Django REST Framework
- [x] Serializers des modèles (Category, Transaction, CategorizationRule) — les vues actuelles construisent les réponses à la main (dicts), pas encore de `serializers.py`
- [x] ViewSets + router (`TransactionViewSet`, `DefaultRouter` dans `config/urls.py`). Pas en lecture seule : des actions d'écriture existent déjà (`categorize`)
- [x] Configurer CORS (`django-cors-headers`) — pas encore fait, bloquant dès que le front tournera sur une origine différente (autre port)
- [x] Testé informellement via curl et l'API navigable DRF pendant le développement (pas de collection Postman formalisée)
- [x] (Authentification différée : mono-utilisateur pour l'instant, voir Phase 8) — confirmé le 2026-07-25

**Décision front (2026-07-25)** : Next.js plutôt que React seul, pour la simplicité du routing (fichier-based) et une formation Next récente. Objectif assumé : une application simple, pas de recherche de perfection technique. Pas de besoin de SSR/App Router avancé identifié pour l'instant, usage prévu en composants client classiques (fetch vers l'API Django).

### 📅 Phase 5 : Import flexible (endpoints) (Probablement abandonné pour la version Python)

Expose le normaliseur paramétrable (Phase 2) via l'API, pour que n'importe quel client
puisse importer un fichier en définissant son mapping.

- [ ] Endpoint d'upload qui renvoie un aperçu (lignes brutes + colonnes détectées)
- [ ] Endpoint d'import qui applique le mapping fourni par le client
- [ ] Modèle `ImportProfile` pour mémoriser et réutiliser un mapping (banque récurrente)

**Décision (2026-07-25)** : pas de changement de banque prévu, la commande dev `import_bank_file` reste suffisante pour l'usage réel. Cette phase serait de toute façon différente sur une version Java du projet, pas d'intérêt à l'investir maintenant côté Python. Reste ici pour mémoire, à reconsidérer seulement si un besoin concret apparaît.

**Précision (2026-07-26)** : ceci ne bloque pas un simple endpoint `POST` d'upload à format fixe pour le front (voir ci-dessous), qui est une toute autre ampleur que le mapping flexible décrit ici.

- [ ] Endpoint `POST` d'upload de fichier bancaire, format fixe (réutilise `excel_importer.py` tel quel), pour que le front n'ait plus besoin de la ligne de commande

### 📅 Phase 6 : Catégories, sous-catégories et budgets (endpoints) (À VENIR)

- [ ] Endpoints CRUD des catégories (hiérarchie parent/enfant, choix du `parent` à la création)
- [ ] Champ booléen "charge fixe" sur `Category`, posé au niveau de la (sous-)catégorie concernée, sans héritage automatique parent → enfant
- [ ] Endpoints CRUD des budgets (aucun endpoint n'existe aujourd'hui)
- [ ] Champ "seuil d'alerte" sur `Budget` (ou équivalent), stocké côté API pour rester partagé entre les deux utilisateurs du foyer
- [ ] Endpoint d'affectation d'une catégorie à une transaction (PATCH)
- [ ] Liste des transactions : pagination (`PageNumberPagination`), paramètre `month=YYYY-MM`, filtre par montant (min/max)

**Note (2026-07-25)** : intérêt confirmé pour creuser les sous-catégories. Le champ `parent` (auto-référence) existe déjà sur `Category`, pas encore exploité par une vue.

**Note (2026-07-26)** : besoin confirmé plus tôt que prévu (avant même l'usage du front), suite à la réflexion sur les charges fixes : une catégorie grossière ("Logement") ne permet pas d'isoler emprunt / assurance emprunteur / assurance maison. Phase reformulée pour regrouper catégories, sous-catégories et budgets, qui doivent de toute façon avancer ensemble (le seuil d'alerte et la charge fixe s'appuient sur ces deux modèles).

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
