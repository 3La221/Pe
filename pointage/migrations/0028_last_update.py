# Generated by Django 5.0.2 on 2024-03-03 09:48

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0027_month_stat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Last_update',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pointage.station')),
            ],
        ),
    ]
