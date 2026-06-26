@echo off
echo ========================================
echo Installation - Gestion de Presence NFC
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Creation de l'environnement virtuel...
python -m venv .venv
if errorlevel 1 (
    echo ERREUR: Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)

echo [2/5] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo [3/5] Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR: Impossible d'installer les dependances
    pause
    exit /b 1
)

echo [4/5] Application des migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERREUR: Impossible d'appliquer les migrations
    pause
    exit /b 1
)

echo [5/5] Configuration terminee!
echo.
echo ========================================
echo Installation terminee avec succes!
echo ========================================
echo.
echo Pour lancer le serveur, executez:
echo   start.bat
echo.
pause
