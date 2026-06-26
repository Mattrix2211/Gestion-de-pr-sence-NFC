"""
Script de démonstration pour tester l'application sans lecteur NFC
Crée des utilisateurs de test et simule des entrées/sorties
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfc_presence.settings')
django.setup()

from presence.models import Utilisateur, HistoriquePresence

def creer_utilisateurs_demo():
    """Créer des utilisateurs de démonstration"""
    utilisateurs_demo = [
        {
            'uid_carte': 'TEST0001',
            'nom': 'MARTIN',
            'prenom': 'JEAN',
            'date_naissance': '1985-03-15',
            'lieu_naissance': 'PARIS',
            'departement_naissance': 'PARIS',
            'pays_naissance': 'FRANCE',
            'nationalite': 'FRANCAISE',
            'entreprise': 'TECH SOLUTIONS',
        },
        {
            'uid_carte': 'TEST0002',
            'nom': 'DURAND',
            'prenom': 'MARIE',
            'date_naissance': '1990-07-22',
            'lieu_naissance': 'LYON',
            'departement_naissance': 'RHONE',
            'pays_naissance': 'FRANCE',
            'nationalite': 'FRANCAISE',
            'entreprise': 'INNOVATION LAB',
        },
        {
            'uid_carte': 'TEST0003',
            'nom': 'BERNARD',
            'prenom': 'PIERRE',
            'date_naissance': '1988-11-03',
            'lieu_naissance': 'MARSEILLE',
            'departement_naissance': 'BOUCHES-DU-RHONE',
            'pays_naissance': 'FRANCE',
            'nationalite': 'FRANCAISE',
            'entreprise': 'DATA CORP',
        },
        {
            'uid_carte': 'TEST0004',
            'nom': 'GARCIA',
            'prenom': 'CARLOS',
            'date_naissance': '1992-01-18',
            'lieu_naissance': 'MADRID',
            'departement_naissance': 'MADRID',
            'pays_naissance': 'ESPAGNE',
            'nationalite': 'ESPAGNOLE',
            'entreprise': 'GLOBAL SYSTEMS',
        },
        {
            'uid_carte': 'TEST0005',
            'nom': 'SMITH',
            'prenom': 'JOHN',
            'date_naissance': '1987-09-12',
            'lieu_naissance': 'LONDON',
            'departement_naissance': 'LONDON',
            'pays_naissance': 'ANGLETERRE',
            'nationalite': 'BRITANNIQUE',
            'entreprise': 'TECH SOLUTIONS',
        }
    ]
    
    print("🚀 Création des utilisateurs de démonstration...")
    
    for data in utilisateurs_demo:
        utilisateur, created = Utilisateur.objects.get_or_create(
            uid_carte=data['uid_carte'],
            defaults=data
        )
        
        if created:
            print(f"✅ Utilisateur créé : {utilisateur.prenom} {utilisateur.nom}")
        else:
            print(f"ℹ️  Utilisateur existant : {utilisateur.prenom} {utilisateur.nom}")

def simuler_historique():
    """Simuler un historique de présences"""
    print("\n📊 Simulation de l'historique des présences...")
    
    utilisateurs = Utilisateur.objects.all()
    
    # Simuler les 7 derniers jours
    for i in range(7):
        date_simulation = datetime.now() - timedelta(days=i)
        
        for utilisateur in utilisateurs:
            # 70% de chance d'être présent un jour donné
            if random.random() < 0.7:
                # Heure d'arrivée entre 8h et 10h
                heure_entree = date_simulation.replace(
                    hour=random.randint(8, 10),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Créer l'entrée
                HistoriquePresence.objects.get_or_create(
                    utilisateur=utilisateur,
                    type_action='ENTREE',
                    horodatage=heure_entree
                )
                
                # 80% de chance de sortir le même jour
                if random.random() < 0.8:
                    # Heure de sortie entre 17h et 19h
                    heure_sortie = date_simulation.replace(
                        hour=random.randint(17, 19),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    
                    HistoriquePresence.objects.get_or_create(
                        utilisateur=utilisateur,
                        type_action='SORTIE',
                        horodatage=heure_sortie
                    )
    
    # Simuler quelques personnes présentes actuellement
    utilisateurs_sample = random.sample(list(utilisateurs), min(2, len(utilisateurs)))
    for utilisateur in utilisateurs_sample:
        utilisateur.present = True
        utilisateur.save()
        
        # Créer une entrée récente
        heure_entree_recent = datetime.now() - timedelta(hours=random.randint(1, 6))
        HistoriquePresence.objects.get_or_create(
            utilisateur=utilisateur,
            type_action='ENTREE',
            horodatage=heure_entree_recent
        )
    
    total_historique = HistoriquePresence.objects.count()
    presents = Utilisateur.objects.filter(present=True).count()
    
    print(f"✅ {total_historique} entrées d'historique créées")
    print(f"✅ {presents} personnes actuellement présentes")

def afficher_statistiques():
    """Afficher les statistiques actuelles"""
    print("\n📈 Statistiques actuelles :")
    print("-" * 40)
    
    total_utilisateurs = Utilisateur.objects.count()
    presents = Utilisateur.objects.filter(present=True).count()
    absents = total_utilisateurs - presents
    total_historique = HistoriquePresence.objects.count()
    entrees = HistoriquePresence.objects.filter(type_action='ENTREE').count()
    sorties = HistoriquePresence.objects.filter(type_action='SORTIE').count()
    
    print(f"👥 Utilisateurs enregistrés : {total_utilisateurs}")
    print(f"✅ Personnes présentes : {presents}")
    print(f"❌ Personnes absentes : {absents}")
    print(f"📊 Total historique : {total_historique}")
    print(f"🔄 Entrées : {entrees}")
    print(f"🔄 Sorties : {sorties}")
    
    if presents > 0:
        print(f"\n👥 Personnes actuellement présentes :")
        for utilisateur in Utilisateur.objects.filter(present=True):
            derniere_entree = HistoriquePresence.objects.filter(
                utilisateur=utilisateur,
                type_action='ENTREE'
            ).order_by('-horodatage').first()
            
            heure = derniere_entree.horodatage.strftime('%H:%M') if derniere_entree else 'N/A'
            print(f"   • {utilisateur.prenom} {utilisateur.nom} ({utilisateur.entreprise}) - Arrivé(e) à {heure}")

def nettoyer_donnees():
    """Nettoyer toutes les données de test"""
    if input("\n⚠️  Voulez-vous supprimer toutes les données de test ? (oui/non): ").lower() == 'oui':
        HistoriquePresence.objects.all().delete()
        Utilisateur.objects.all().delete()
        print("🗑️  Toutes les données ont été supprimées")
    else:
        print("ℹ️  Suppression annulée")

def main():
    """Fonction principale"""
    print("=" * 50)
    print("🎯 SCRIPT DE DÉMONSTRATION NFC PRÉSENCE")
    print("=" * 50)
    
    while True:
        print("\n📋 Que voulez-vous faire ?")
        print("1. Créer des utilisateurs de démonstration")
        print("2. Simuler un historique de présences")
        print("3. Afficher les statistiques")
        print("4. Nettoyer toutes les données")
        print("5. Tout créer (utilisateurs + historique)")
        print("0. Quitter")
        
        choix = input("\n👉 Votre choix (0-5) : ").strip()
        
        if choix == '1':
            creer_utilisateurs_demo()
        elif choix == '2':
            simuler_historique()
        elif choix == '3':
            afficher_statistiques()
        elif choix == '4':
            nettoyer_donnees()
        elif choix == '5':
            creer_utilisateurs_demo()
            simuler_historique()
            afficher_statistiques()
        elif choix == '0':
            print("\n👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide")
    
    print("\n🌐 Vous pouvez maintenant tester l'application sur http://127.0.0.1:8000/")
    print("🔑 Mot de passe admin : admin123")

if __name__ == '__main__':
    main()