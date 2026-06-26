from django.contrib import admin
from .models import Utilisateur, HistoriquePresence, ConfigurationSession, BadgeVisiteur

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'societe_raison', 'present', 'date_creation']
    list_filter = ['present', 'nationalite', 'date_creation']
    search_fields = ['nom', 'prenom', 'societe_raison', 'uid_carte']
    readonly_fields = ['uid_carte', 'date_creation', 'date_modification']
    ordering = ['nom', 'prenom']

    fieldsets = (
        ('Informations de la carte', {
            'fields': ('uid_carte',)
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'nationalite')
        }),
        ('Lieu de naissance', {
            'fields': ('lieu_naissance', 'departement_pays')
        }),
        ('Professionnel', {
            'fields': ('societe_raison',)
        }),
        ('Statut', {
            'fields': ('present',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

@admin.register(HistoriquePresence)
class HistoriquePresenceAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type_action', 'horodatage']
    list_filter = ['type_action', 'horodatage']
    search_fields = ['utilisateur__nom', 'utilisateur__prenom', 'utilisateur__societe_raison']
    readonly_fields = ['horodatage']
    ordering = ['-horodatage']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('utilisateur')

@admin.register(ConfigurationSession)
class ConfigurationSessionAdmin(admin.ModelAdmin):
    list_display = ['cle', 'valeur', 'date_modification']
    readonly_fields = ['date_modification']


@admin.register(BadgeVisiteur)
class BadgeVisiteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'uid_carte', 'affecte_a', 'date_attribution', 'date_creation']
    search_fields = ['nom', 'uid_carte', 'affecte_a__nom', 'affecte_a__prenom', 'affecte_a__societe_raison']
    list_filter = ['date_creation']
    autocomplete_fields = ['affecte_a']
