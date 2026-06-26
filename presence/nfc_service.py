"""
Service NFC pour lire les cartes avec le lecteur ACR122U.
Deux backends:
- PC/SC local (pyscard) pour Linux/WSL.
- Agent HTTP distant (sur l'hôte Windows) pour un usage Docker Windows simplifié.
"""
import threading
import time
import logging
import os

try:
    import requests  # utilisé pour le backend agent
except Exception:  # fallback si non installé dans certains contextes
    requests = None

logger = logging.getLogger(__name__)


try:
    # Imports PC/SC optionnels; absents dans le conteneur (backend agent)
    from smartcard.CardMonitoring import CardMonitor, CardObserver  # type: ignore
    from smartcard.util import toHexString as sc_toHexString  # type: ignore
    from smartcard.System import readers as sc_readers  # type: ignore
    from smartcard.CardConnection import CardConnection  # type: ignore
    HAVE_PYSCARD = True
except Exception:
    HAVE_PYSCARD = False
    CardMonitor = None
    CardObserver = object  # évite erreur de sous-classement si utilisé par erreur
    sc_toHexString = None
    sc_readers = None
    CardConnection = None


class NFCCardObserver(CardObserver):
    """Observer pour détecter l'insertion de cartes NFC (utilisé uniquement si pyscard dispo)."""

    def __init__(self, callback=None):
        self.callback = callback
        self.last_uid = None

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            try:
                card.connection = card.createConnection()
                card.connection.connect()
                uid = self._get_card_uid(card.connection)
                if uid and uid != self.last_uid:
                    self.last_uid = uid
                    if self.callback:
                        self.callback(uid)
            except Exception as e:
                logger.error(f"Erreur lors de la lecture de la carte: {e}")
        for _ in removedcards:
            self.last_uid = None

    def _get_card_uid(self, connection):
        try:
            command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(command)
            if sw1 == 0x90 and sw2 == 0x00 and sc_toHexString:
                uid = sc_toHexString(data).replace(' ', '')
                return uid
            logger.warning(f"Erreur lors de la lecture UID: SW1={sw1:02X}, SW2={sw2:02X}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la lecture UID: {e}")
            return None


class NFCService:
    """Service principal pour la gestion NFC"""
    
    def __init__(self):
        self.monitor = None
        self.observer = None
        self.is_monitoring = False
        self.last_uid = None
        self.card_detected_callback = None
        
    def start_monitoring(self, callback=None):
        """Démarrer la surveillance des cartes NFC"""
        try:
            if self.is_monitoring:
                return
                
            self.card_detected_callback = callback
            
            if not HAVE_PYSCARD:
                raise Exception("pyscard non disponible (backend PC/SC)")
            # Vérifier qu'il y a des lecteurs disponibles
            available_readers = sc_readers()
            if not available_readers:
                raise Exception("Aucun lecteur de cartes détecté")
            
            logger.info(f"Lecteurs disponibles: {[str(r) for r in available_readers]}")
            
            # Créer l'observer
            self.observer = NFCCardObserver(callback=self._card_detected)
            
            # Démarrer le monitoring
            self.monitor = CardMonitor() if HAVE_PYSCARD else None
            self.monitor.addObserver(self.observer)
            
            self.is_monitoring = True
            logger.info("Surveillance NFC démarrée")
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la surveillance NFC: {e}")
            raise
    
    def start_continuous_monitoring(self):
        """Démarrer la surveillance continue en arrière-plan"""
        import threading
        import time
        
        def monitor_loop():
            """Boucle de surveillance continue"""
            last_uid = None
            last_detection_time = 0
            card_present = False
            consecutive_empty_reads = 0
            
            while self.is_monitoring:
                try:
                    if not HAVE_PYSCARD:
                        time.sleep(0.5)
                        continue
                    available_readers = sc_readers()
                    if available_readers:
                        reader = available_readers[0]
                        connection = reader.createConnection()
                        connection.connect()
                        
                        try:
                            # Commande pour lire l'UID
                            command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                            data, sw1, sw2 = connection.transmit(command)
                            
                            if sw1 == 0x90 and sw2 == 0x00:
                                if sc_toHexString is None:
                                    continue
                                uid = sc_toHexString(data).replace(' ', '')
                                current_time = time.time()
                                
                                # Reset compteur de lectures vides
                                consecutive_empty_reads = 0
                                
                                # Nouvelle carte détectée
                                if not card_present or uid != last_uid:
                                    # Éviter les détections multiples rapides (debouncing)
                                    if (current_time - last_detection_time) > 1.5:
                                        last_uid = uid
                                        last_detection_time = current_time
                                        card_present = True
                                        
                                        if self.card_detected_callback:
                                            self.card_detected_callback(uid)
                                            
                        except Exception:
                            # Pas de carte sur le lecteur
                            consecutive_empty_reads += 1
                            # Considérer que la carte est retirée après plusieurs lectures vides
                            if consecutive_empty_reads > 3 and card_present:
                                card_present = False
                                last_uid = None
                                logger.debug("Carte retirée du lecteur")
                        
                        connection.disconnect()
                        
                except Exception as e:
                    # Erreur de connexion au lecteur, ne pas spammer les logs
                    logger.debug(f"Lecteur non disponible: {e}")
                    consecutive_empty_reads += 1
                
                time.sleep(0.3)  # Pause courte entre les lectures
        
        if not self.is_monitoring:
            self.is_monitoring = True
            monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            monitor_thread.start()
            logger.info("Surveillance continue démarrée")
    
    def stop_monitoring(self):
        """Arrêter la surveillance des cartes NFC"""
        try:
            if self.monitor and self.observer:
                self.monitor.deleteObserver(self.observer)
                self.is_monitoring = False
                logger.info("Surveillance NFC arrêtée")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la surveillance NFC: {e}")
    
    def _card_detected(self, uid):
        """Callback interne appelé quand une carte est détectée"""
        self.last_uid = uid
        if self.card_detected_callback:
            self.card_detected_callback(uid)
    
    def lire_carte(self):
        """Lire une carte NFC de manière synchrone"""
        try:
            if not HAVE_PYSCARD:
                return None
            available_readers = sc_readers()
            if not available_readers:
                return None  # Pas d'erreur, juste pas de lecteur
            
            # Utiliser le premier lecteur disponible
            reader = available_readers[0]
            
            try:
                # Se connecter au lecteur
                connection = reader.createConnection()
                connection.connect()
                
                # Lire l'UID
                uid = self._get_card_uid_direct(connection)
                
                connection.disconnect()
                return uid  # Peut être None si pas de carte, ce n'est pas une erreur
                        
            except Exception as e:
                # Pas de carte ou problème de connexion - ce n'est pas forcément une erreur
                if "La carte à puce a été supprimée" in str(e):
                    return None  # Pas de carte, c'est normal
                else:
                    logger.debug(f"Erreur de lecture NFC: {e}")
                    return None
            
        except Exception as e:
            logger.debug(f"Erreur lors de la lecture directe: {e}")
            return None
    
    def _get_card_uid_direct(self, connection):
        """Lire l'UID directement depuis une connexion"""
        try:
            # Commande APDU pour obtenir l'UID
            command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            
            data, sw1, sw2 = connection.transmit(command)
            
            if sw1 == 0x90 and sw2 == 0x00 and sc_toHexString:
                uid = sc_toHexString(data).replace(' ', '')
                logger.info(f"UID lu: {uid}")
                return uid
            else:
                logger.warning(f"Erreur lecture UID: SW1={sw1:02X}, SW2={sw2:02X}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lecture UID directe: {e}")
            return None
    
    def test_connection(self):
        """Tester la connexion avec le lecteur NFC"""
        try:
            if not HAVE_PYSCARD:
                return False, "pyscard indisponible"
            available_readers = sc_readers()
            if not available_readers:
                return False, "Aucun lecteur de cartes détecté"

            # Le lecteur est présent, on considère qu'il est connecté
            # Pas besoin de tester la connexion réelle car ça peut échouer sans carte
            reader = available_readers[0]
            return True, f"Lecteur {reader} connecté"
            
        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"


# Instance globale du service NFC
nfc_service_instance = None

def get_nfc_service():
    """Obtenir l'instance globale du service NFC en fonction de NFC_BACKEND.
    NFC_BACKEND=agent  -> RemoteNFCService (requiert requests)
    NFC_BACKEND=pcsc   -> NFCService (par défaut)
    """
    global nfc_service_instance
    if nfc_service_instance is not None:
        return nfc_service_instance
    backend = os.getenv('NFC_BACKEND', 'pcsc').lower()
    if backend == 'agent':
        nfc_service_instance = RemoteNFCService(
            base_url=os.getenv('NFC_AGENT_URL', 'http://host.docker.internal:8765')
        )
    else:
        nfc_service_instance = NFCService()
    return nfc_service_instance


class RemoteNFCService:
    """Backend qui interroge un agent HTTP local sur l'hôte Windows.
    L'agent expose /status et /uid.
    """
    def __init__(self, base_url: str = 'http://host.docker.internal:8765'):
        self.base_url = base_url.rstrip('/')

    def start_continuous_monitoring(self, callback=None):
        # Rien à faire: l'agent gère la lecture en continu côté hôte
        return

    def stop_monitoring(self):
        return

    def test_connection(self):
        if requests is None:
            return False, "Le backend agent requiert le module requests"
        try:
            r = requests.get(f"{self.base_url}/status", timeout=1.5)
            if r.status_code == 200:
                data = r.json()
                return bool(data.get('reader_connected', False)), "Agent joignable"
            return False, f"Statut HTTP {r.status_code}"
        except Exception as e:
            return False, f"Agent indisponible: {e}"

    def lire_carte(self):
        if requests is None:
            return None
        try:
            r = requests.get(f"{self.base_url}/uid", timeout=1.5)
            if r.status_code != 200:
                return None
            data = r.json()
            # Retourne l'UID courant si une carte est présente; sinon None
            return (data.get('uid') or '').strip() or None
        except Exception:
            return None