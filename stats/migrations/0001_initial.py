# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 21:36
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='game_avatars')),
                ('basedir', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('ip', models.GenericIPAddressField(unpack_ipv4=True)),
                ('port', models.PositiveIntegerField(default=27015)),
                ('hostname', models.TextField(blank=True, max_length=200, null=True)),
                ('secret_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='LogTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('pretty', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServerLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=200)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='logs', to='stats.GameServer')),
                ('tags', models.ManyToManyField(to='stats.LogTag')),
            ],
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('identifier', models.PositiveIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='teams',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stats.Teams'),
        ),
    ]
