# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 21:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameserver',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.Game'),
        ),
    ]
