"""
Test simple du lecteur NFC ACR122U
Ce script teste la connexion et la lecture de cartes NFC
"""

from smartcard.System import readers
from smartcard.util import toHexString
import time

def test_lecteur_nfc():
    """Tester la connexion avec le lecteur NFC"""
    print("🔍 Test du lecteur NFC ACR122U")
    print("=" * 40)
    
    try:
        # Lister les lecteurs disponibles
        available_readers = readers()
        print(f"📡 Lecteurs détectés : {len(available_readers)}")
        
        if not available_readers:
            print("❌ Aucun lecteur de cartes détecté")
            print("💡 Vérifiez que votre lecteur ACR122U est bien branché")
            return False
        
        for i, reader in enumerate(available_readers):
            print(f"   {i+1}. {reader}")
        
        # Utiliser le premier lecteur
        reader = available_readers[0]
        print(f"\n🎯 Utilisation du lecteur : {reader}")
        
        # Test de lecture de carte
        print("\n💳 Placez une carte NFC sur le lecteur...")
        print("⏱️  Tentative de lecture pendant 15 secondes...")
        
        for tentative in range(15):
            try:
                # Tenter de se connecter à chaque fois (plus robuste)
                connection = reader.createConnection()
                connection.connect()
                
                # Commande pour lire l'UID de la carte
                command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(command)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data).replace(' ', '')
                    print(f"🎉 CARTE DÉTECTÉE !")
                    print(f"🆔 UID de la carte : {uid}")
                    connection.disconnect()
                    return uid
                else:
                    print(f"📡 Lecteur prêt, en attente d'une carte... (tentative {tentative + 1}/15)")
                    
                connection.disconnect()
                    
            except Exception as e:
                if "La carte à puce a été supprimée" in str(e):
                    print(f"📡 Lecteur prêt, en attente d'une carte... (tentative {tentative + 1}/15)")
                else:
                    print(f"⚠️  Erreur: {e}")
            
            time.sleep(1)
        
        print("⚠️  Aucune carte détectée dans le temps imparti")
        print("💡 Assurez-vous qu'une carte NFC est bien placée sur le lecteur")
        return None
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def test_multiple_cartes():
    """Test en boucle pour lire plusieurs cartes"""
    print("\n🔄 Mode test continu")
    print("Placez et retirez des cartes pour tester...")
    print("Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        available_readers = readers()
        if not available_readers:
            print("❌ Aucun lecteur disponible")
            return
            
        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()
        
        cartes_detectees = set()
        
        while True:
            try:
                command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(command)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    uid = toHexString(data).replace(' ', '')
                    
                    if uid not in cartes_detectees:
                        cartes_detectees.add(uid)
                        print(f"🆕 Nouvelle carte : {uid}")
                        print(f"📊 Total cartes détectées : {len(cartes_detectees)}")
                    
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n👋 Test arrêté par l'utilisateur")
                break
            except Exception:
                # Pas de carte, continuer
                time.sleep(0.5)
        
        connection.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == '__main__':
    print("🎯 TEST DU LECTEUR NFC ACR122U")
    print("=" * 50)
    
    # Test de base
    resultat = test_lecteur_nfc()
    
    if resultat:
        # Si ça marche, proposer le test continu
        choix = input("\n❓ Voulez-vous tester en mode continu ? (o/n) : ").lower()
        if choix == 'o':
            test_multiple_cartes()
    
    print("\n✅ Test terminé")
    print("💡 Si le test fonctionne, votre lecteur est prêt pour l'application Django !")