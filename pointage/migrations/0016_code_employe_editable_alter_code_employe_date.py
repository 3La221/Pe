# Generated by Django 5.0.2 on 2024-02-22 16:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0015_alter_code_employe_date_alter_code_employe_employe'),
    ]

    operations = [
        migrations.AddField(
            model_name='code_employe',
            name='editable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='code_employe',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 2, 22, 17, 28, 21, 765608)),
        ),
    ]
