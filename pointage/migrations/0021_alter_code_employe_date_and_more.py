# Generated by Django 5.0.2 on 2024-02-28 16:17

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0020_alter_code_employe_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code_employe',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='employe',
            name='Date_Recrutement',
            field=models.DateField(default=datetime.datetime(2024, 2, 28, 16, 17, 18, 252795, tzinfo=datetime.timezone.utc)),
        ),
    ]
