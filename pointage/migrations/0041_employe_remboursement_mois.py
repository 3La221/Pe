# Generated by Django 5.0.2 on 2024-03-14 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0040_remove_employe_remboursement_mois'),
    ]

    operations = [
        migrations.AddField(
            model_name='employe',
            name='remboursement_mois',
            field=models.IntegerField(default=0),
        ),
    ]
