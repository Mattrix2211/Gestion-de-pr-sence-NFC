# Gestion de Présence NFC

Application web Django pour la gestion des présences via lecteur NFC. Les utilisateurs badgent à l'entrée et à la sortie avec leurs cartes NFC ; l'application suit les présences en temps réel, génère des statistiques et gère les badges visiteurs.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Démarrage rapide (Docker + Windows)](#démarrage-rapide-docker--windows)
- [Installation locale (sans Docker)](#installation-locale-sans-docker)
- [Architecture NFC](#architecture-nfc)
- [Variables d'environnement](#variables-denvironnement)
- [Pages de l'application](#pages-de-lapplication)
- [Structure du projet](#structure-du-projet)
- [Déploiement en production](#déploiement-en-production)
- [Dépannage](#dépannage)

---

## Fonctionnalités

### Mode Utilisateur
- Badgeage NFC sans clic — l'écoute est continue et automatique
- Compteur en temps réel des personnes présentes
- Tableau des présents avec heure d'arrivée
- Aide contextuelle intégrée (bouton **i**)

### Mode Administrateur
- Gestion complète des utilisateurs (CRUD, recherche, blacklist)
- Import/Export Excel des utilisateurs et de l'historique
- Workflow de validation : import en attente → validation admin
- Détachement de carte NFC sans supprimer l'utilisateur
- Historique détaillé des entrées/sorties
- Statistiques avancées : courbes 24h glissantes + heatmap 7×24
- Paramètres de rétention des données configurables (historique, logs, utilisateurs inactifs)
- Purge immédiate depuis l'interface

### Badges visiteurs
- Inventaire dédié avec nom optionnel par badge
- Affectation depuis l'accueil : scanner un badge libre ouvre une popup de sélection ou création d'utilisateur
- Réinitialisation automatique des affectations chaque jour à 00:00
- Gestion (ajout/suppression/désaffectation) réservée aux admins ; l'affectation est accessible à tous

---

## Prérequis

| Composant | Version minimale |
|---|---|
| Python | 3.11+ |
| Docker Desktop | Dernière version (pour le déploiement Windows) |
| Lecteur NFC | ACR122U (ISO 14443A / RFID 13.56 MHz) |

---

## Démarrage rapide (Docker + Windows)

C'est la méthode recommandée sur Windows. Un agent Python tourne sur l'hôte et expose l'UID de la carte via HTTP ; le conteneur Docker interroge cet agent sans avoir besoin d'accès USB direct.

### 1. Démarrer l'agent NFC (terminal 1)

```powershell
python -m venv .agentvenv
.\.agentvenv\Scripts\Activate.ps1
pip install pyscard
python tools\nfc_agent_windows.py
```

L'agent écoute sur `http://127.0.0.1:8765`. Vérification : `Invoke-RestMethod http://127.0.0.1:8765/uid`

### 2. Lancer l'application (terminal 2)

```powershell
docker compose up --build
```

Ouvrez **http://localhost:8000**. Les migrations sont appliquées automatiquement au démarrage.

### 3. Arrêter proprement

```powershell
docker compose down
```

### Commandes Docker utiles

```powershell
docker compose restart              # Redémarrage rapide
docker compose logs -f web          # Logs en direct
docker compose exec web sh          # Shell dans le conteneur
docker compose exec web python manage.py migrate  # Migrations manuelles
```

---

## Installation locale (sans Docker)

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
# ou : .\.venv\Scripts\Activate.ps1   # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Application accessible sur `http://127.0.0.1:8000/`.

> **Mot de passe admin par défaut :** `admin123` (modifiable via l'interface Paramètres)

---

## Architecture NFC

Le service NFC (`presence/nfc_service.py`) supporte deux backends, sélectionnables via la variable `NFC_BACKEND` :

| Backend | Valeur | Usage |
|---|---|---|
| Agent HTTP | `agent` (défaut) | Docker sur Windows — interroge `NFC_AGENT_URL` |
| PC/SC direct | `pcsc` | Linux/WSL — accès direct via pyscard |

Le service effectue une **détection sur front montant** : l'UID n'est retourné que lors de la première présentation d'une carte, pas sur les lectures répétées.

**Priorité de résolution :** si un UID correspond à un badge visiteur, le flux visiteur (affectation/pointage) est traité en priorité avant toute recherche d'utilisateur par carte personnelle.

---

## Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `NFC_BACKEND` | `agent` | Backend NFC : `agent` ou `pcsc` |
| `NFC_AGENT_URL` | `http://host.docker.internal:8765` | URL de l'agent NFC (mode Docker) |
| `SECRET_KEY` | valeur de développement | **À remplacer en production** |
| `DEBUG` | `True` | Mettre à `False` en production |

Créez un fichier `.env` à la racine pour surcharger ces valeurs (ne pas le committer).

---

## Pages de l'application

| Page | Route | Accès |
|---|---|---|
| Accueil | `/` | Tous |
| Utilisateurs | `/utilisateurs/` | Admin |
| Badges visiteurs | `/visiteur/` | Admin |
| Historique | `/historique/` | Admin |
| Statistiques | `/statistiques/` | Admin |
| Paramètres | `/parametres/` | Admin |
| Logs | `/logs/` | Admin |

---

## Structure du projet

```
.
├── nfc_presence/               # Configuration Django (settings, urls, wsgi)
├── presence/                   # Application principale
│   ├── models.py               # 4 modèles : Utilisateur, HistoriquePresence,
│   │                           #   ConfigurationSession, BadgeVisiteur
│   ├── views.py                # Logique métier (NFC, présences, CRUD, stats…)
│   ├── urls.py                 # 40+ routes (pages + API JSON)
│   ├── nfc_service.py          # Abstraction backend NFC
│   └── migrations/             # Migrations Django
├── templates/presence/         # Templates HTML (Bootstrap 5 + Chart.js)
├── static/                     # CSS, JS, fonts (pré-bundlés, sans pipeline)
├── tools/
│   └── nfc_agent_windows.py    # Agent Windows : lit le lecteur et expose l'UID via HTTP
├── docker/
│   └── entrypoint.sh           # Migrations auto + lancement du serveur
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Déploiement en production

1. Définir une `SECRET_KEY` forte et unique
2. Passer `DEBUG = False`
3. Renseigner `ALLOWED_HOSTS`
4. Remplacer SQLite par PostgreSQL ou MySQL
5. Configurer HTTPS (reverse proxy Nginx/Caddy)
6. Changer le mot de passe admin depuis l'interface Paramètres

---

## Dépannage

| Symptôme | Solution |
|---|---|
| L'agent ne démarre pas | Vérifier que `pyscard` est installé et que le lecteur est reconnu par Windows |
| "Lecteur déconnecté" dans l'app | S'assurer que l'agent écoute sur 8765 ; vérifier `NFC_AGENT_URL` |
| "DisallowedHost" | Ajouter l'hôte à `ALLOWED_HOSTS` dans `nfc_presence/settings.py` |
| Erreur de migration | Lancer `python manage.py migrate --run-syncdb` |

---

**Version :** 1.5 — **Compatibilité :** Windows 10/11 · Python 3.11+ · Django 5.2
