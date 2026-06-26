from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('utilisateurs/', views.utilisateurs, name='utilisateurs'),
    path('visiteur/', views.visiteurs, name='visiteurs'),
    path('historique/', views.historique, name='historique'),
    path('statistiques/', views.statistiques, name='statistiques'),
    path('parametres/', views.parametres, name='parametres'),
    path('logs/', views.logs_page, name='logs_page'),
    path('logs/clear/', views.clear_logs, name='logs_clear'),
    path('purge/', views.purge_now, name='purge_now'),
    
    # Authentification admin
    path('toggle-admin/', views.toggle_admin_mode, name='toggle_admin'),
    
    # API NFC
    path('api/lire-carte/', views.lire_carte_nfc, name='lire_carte_nfc'),
    path('api/ecoute-nfc/', views.ecoute_nfc_continue, name='ecoute_nfc_continue'),
    path('api/nfc/read-uid/', views.nfc_lire_uid, name='nfc_lire_uid'),
    path('api/enregistrer-utilisateur/', views.enregistrer_utilisateur, name='enregistrer_utilisateur'),
    
    # API Gestion utilisateurs
    path('api/utilisateur/<int:user_id>/', views.get_utilisateur_data, name='get_utilisateur_data'),
    path('api/utilisateur/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('api/utilisateur/<int:user_id>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('api/utilisateur/<int:user_id>/blacklist/', views.toggle_blacklist, name='toggle_blacklist'),
    path('api/utilisateur/<int:user_id>/detacher-carte/', views.detacher_carte, name='detacher_carte'),
    path('api/utilisateur/<int:user_id>/lier-carte/', views.lier_carte, name='lier_carte'),
    path('api/utilisateur/<int:user_id>/valider/', views.valider_utilisateur, name='valider_utilisateur'),
    path('api/utilisateur/<int:user_id>/refuser/', views.refuser_utilisateur, name='refuser_utilisateur'),
    path('api/badge/lier-utilisateur/', views.lier_badge_utilisateur_permanent, name='lier_badge_utilisateur_permanent'),
    
    # API Actions administratives
    path('api/vider-presences/', views.vider_liste_presences, name='vider_liste_presences'),
    path('api/forcer-sortie/', views.forcer_sortie_utilisateur, name='forcer_sortie_utilisateur'),
    path('api/supprimer-tous-utilisateurs/', views.supprimer_tous_utilisateurs, name='supprimer_tous_utilisateurs'),
    path('api/vider-historique/', views.vider_historique, name='vider_historique'),

    # API Badges visiteurs (admin)
    path('api/visiteur/ajouter/', views.visiteur_ajouter_badge, name='visiteur_ajouter_badge'),
    path('api/visiteur/<int:badge_id>/supprimer/', views.visiteur_supprimer_badge, name='visiteur_supprimer_badge'),
    path('api/visiteur/<int:badge_id>/desaffecter/', views.visiteur_desaffecter_badge, name='visiteur_desaffecter_badge'),
    path('api/visiteur/affecter/', views.visiteur_affecter_badge, name='visiteur_affecter_badge'),
    path('api/utilisateurs/liste/', views.utilisateurs_liste, name='utilisateurs_liste'),
    
    # Exports Excel
    path('export/utilisateurs/', views.export_utilisateurs_excel, name='export_utilisateurs_excel'),
    path('export/utilisateurs/attente/', views.export_utilisateurs_attente_excel, name='export_utilisateurs_attente_excel'),
    path('export/historique/', views.export_historique_excel, name='export_historique_excel'),
    # Import Excel
    path('api/import/utilisateurs/', views.import_utilisateurs_excel, name='import_utilisateurs_excel'),
    path('api/import/utilisateurs-attente/', views.import_utilisateurs_attente_excel, name='import_utilisateurs_attente_excel'),
]