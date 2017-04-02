# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 21:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_gameserver_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='teams',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stats.Teams'),
        ),
        migrations.AlterField(
            model_name='gameserver',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.Game'),
        ),
        migrations.AlterField(
            model_name='serverlog',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='logs', to='stats.GameServer'),
        ),
    ]