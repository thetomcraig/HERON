# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2020-02-26 06:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0006_auto_20200226_0630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitterpostcache',
            name='cache',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cache', to='bots.SentenceCache'),
        ),
    ]
