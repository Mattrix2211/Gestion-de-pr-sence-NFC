# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presence', '0004_badgevisiteur_nom'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='statut_validation',
            field=models.CharField(
                choices=[('EN_ATTENTE', 'En attente de validation'), ('VALIDE', 'Validé')],
                default='VALIDE',
                max_length=20,
                verbose_name='Statut de validation'
            ),
        ),
    ]
