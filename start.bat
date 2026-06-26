@echo off
echo ========================================
echo Demarrage - Gestion de Presence NFC
echo ========================================
echo.

REM Activer l'environnement virtuel
if not exist .venv\Scripts\activate.bat (
    echo ERREUR: Environnement virtuel non trouve
    echo Executez d'abord install.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Demarrage du serveur Django...
echo.
echo Le serveur sera accessible a : http://127.0.0.1:8000/
echo.
echo Appuyez sur CTRL+C pour arreter le serveur
echo.
python manage.py runserver

pause
