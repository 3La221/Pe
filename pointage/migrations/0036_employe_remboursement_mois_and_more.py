# Generated by Django 5.0.2 on 2024-03-03 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0035_code_employe_stored'),
    ]

    operations = [
        migrations.AddField(
            model_name='employe',
            name='remboursement_mois',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='employe',
            name='remboursement_total',
            field=models.IntegerField(default=0),
        ),
    ]
