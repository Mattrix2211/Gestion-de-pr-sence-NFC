# Guide d'installation - Système de Gestion de Présence NFC

## Prérequis
- Python 3.8 ou supérieur
- Un lecteur NFC compatible (optionnel pour le déploiement initial)

## Étapes d'installation

### 1. Copier le projet
Copiez l'intégralité du dossier `NFC_WEB1.7` sur le nouvel ordinateur.

### 2. Installer Python
Téléchargez et installez Python depuis https://www.python.org/downloads/
- Cochez "Add Python to PATH" lors de l'installation

### 3. Créer l'environnement virtuel
Ouvrez PowerShell dans le dossier du projet et exécutez :
```powershell
python -m venv .venv
```

### 4. Activer l'environnement virtuel
```powershell
.\.venv\Scripts\Activate.ps1
```

Si vous avez une erreur de stratégie d'exécution, exécutez d'abord :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. Installer les dépendances
```powershell
pip install django django-cors-headers nfcpy openpyxl
```

### 6. Appliquer les migrations de base de données
```powershell
python manage.py migrate
```

### 7. Lancer le serveur
```powershell
python manage.py runserver
```

Le serveur sera accessible à l'adresse : http://127.0.0.1:8000/

## Configuration du lecteur NFC

Le lecteur NFC fonctionne automatiquement via PC/SC (pyscard).
Assurez-vous simplement que :
- Le lecteur est branché en USB
- Les pilotes du lecteur sont installés (téléchargez-les depuis le site du fabricant si nécessaire)

## Connexion administrateur
- Par défaut, il n'y a pas d'utilisateur admin créé
- Accédez à l'interface web et créez votre premier utilisateur admin via les paramètres

## Résolution de problèmes

### Erreur : Module non trouvé
Vérifiez que l'environnement virtuel est activé (vous devez voir `(.venv)` au début de votre ligne de commande)

### Le lecteur NFC ne fonctionne pas
- Vérifiez que le lecteur est bien branché
- Vérifiez que `pyscard` est installé : `pip list | findstr pyscard`
- Installez les pilotes du lecteur si nécessaire (ex: ACR122U sur acs.com.hk)
- Redémarrez le serveur après avoir branché le lecteur

### L'application ne charge pas correctement
- Tous les fichiers CSS/JS sont maintenant locaux, l'application fonctionne **sans connexion internet**
- Vérifiez que le serveur Django est bien démarré

## Fichiers importants

- `db.sqlite3` : Base de données (contient tous les utilisateurs et l'historique)
- `static/` : Fichiers CSS, JavaScript et polices (fonctionnent hors ligne)
- `logs/app.log` : Fichier de logs de l'application
- `requirements.txt` : Liste des dépendances Python

## Sauvegarde

Pour sauvegarder vos données, copiez ces fichiers :
- `db.sqlite3` (base de données)
- `logs/` (historiques)

## ⚠️ Important : Déploiement sur un autre ordinateur

**À COPIER :**
- Tous les fichiers du projet (code, templates, static, etc.)
- Le fichier `db.sqlite3` (base de données)
- Les dossiers `logs/` et `static/` (si modifiés)

**NE PAS COPIER :**
- Le dossier `.venv` (environnement virtuel)

**Pourquoi ?** L'environnement virtuel contient des chemins absolus spécifiques à votre ordinateur. Il doit être **recréé** sur chaque nouvel ordinateur en exécutant `install.bat`.
