from django.db import models
from django.utils import timezone


class Utilisateur(models.Model):
    """Modèle pour stocker les informations des utilisateurs NFC"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('VALIDE', 'Validé'),
    ]
    
    uid_carte = models.CharField(max_length=32, unique=True, verbose_name="UID de la carte")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    lieu_naissance = models.CharField(max_length=100, verbose_name="Lieu de naissance")
    departement_pays = models.CharField(max_length=150, verbose_name="Département/Pays", default="")
    nationalite = models.CharField(max_length=100, verbose_name="Nationalité")
    societe_raison = models.CharField(max_length=200, verbose_name="Société/Raison de la visite", default="")
    present = models.BooleanField(default=False, verbose_name="Présent")
    blackliste = models.BooleanField(default=False, verbose_name="Blacklisté")
    statut_validation = models.CharField(max_length=20, choices=STATUT_CHOICES, default='VALIDE', verbose_name="Statut de validation")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Sauvegarder toutes les données en majuscules"""
        if self.uid_carte:
            self.uid_carte = self.uid_carte.upper()
        self.nom = self.nom.upper()
        self.prenom = self.prenom.upper()
        self.lieu_naissance = self.lieu_naissance.upper()
        self.departement_pays = self.departement_pays.upper()
        self.nationalite = self.nationalite.upper()
        self.societe_raison = self.societe_raison.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.societe_raison}"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['nom', 'prenom']


class HistoriquePresence(models.Model):
    """Modèle pour l'historique des entrées et sorties"""
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    ]
    
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, verbose_name="Utilisateur")
    type_action = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type d'action")
    horodatage = models.DateTimeField(default=timezone.now, verbose_name="Date et heure")
    
    def __str__(self):
        return f"{self.utilisateur.prenom} {self.utilisateur.nom} - {self.type_action} - {self.horodatage.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Historique de présence"
        verbose_name_plural = "Historiques de présence"
        ordering = ['-horodatage']


class ConfigurationSession(models.Model):
    """Modèle pour gérer la session admin"""
    cle = models.CharField(max_length=50, unique=True)
    valeur = models.TextField()
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cle}: {self.valeur}"

    class Meta:
        verbose_name = "Configuration de session"
        verbose_name_plural = "Configurations de session"


class BadgeVisiteur(models.Model):
    """Badge visiteur pouvant être affecté/désaffecté à un Utilisateur."""
    uid_carte = models.CharField(max_length=32, unique=True, verbose_name="UID du badge visiteur")
    nom = models.CharField(max_length=100, blank=True, default='', verbose_name="Nom du badge")
    affecte_a = models.ForeignKey(Utilisateur, null=True, blank=True, on_delete=models.SET_NULL, related_name='badges_visiteurs', verbose_name="Affecté à")
    date_attribution = models.DateTimeField(null=True, blank=True, verbose_name="Date d'attribution")
    commentaire = models.CharField(max_length=200, blank=True, default='', verbose_name="Commentaire")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.uid_carte:
            self.uid_carte = self.uid_carte.upper()
        if self.nom:
            self.nom = self.nom.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        label = self.nom or self.uid_carte
        if self.affecte_a:
            return f"BadgeVisiteur {label} -> {self.affecte_a.prenom} {self.affecte_a.nom}"
        return f"BadgeVisiteur {label} (libre)"

    class Meta:
        verbose_name = "Badge visiteur"
        verbose_name_plural = "Badges visiteurs"
        ordering = ['uid_carte']
