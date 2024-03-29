# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2020-02-26 06:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0005_twitterpost_retweet'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentenceCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word1', models.CharField(default=b'PLACEHOLDER', max_length=1000, null=True)),
                ('word2', models.CharField(default=b'PLACEHOLDER', max_length=1000, null=True)),
                ('final_word', models.CharField(default=b'PLACEHOLDER', max_length=1000, null=True)),
                ('beginning', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='twitterpostcache',
            name='final_word',
        ),
        migrations.RemoveField(
            model_name='twitterpostcache',
            name='word1',
        ),
        migrations.RemoveField(
            model_name='twitterpostcache',
            name='word2',
        ),
        migrations.AddField(
            model_name='twitterpost',
            name='template',
            field=models.CharField(default=b'PLACEHOLDER', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='twitterpostcache',
            name='cache',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='bots.SentenceCache'),
        ),
        migrations.AddField(
            model_name='twitterpostcache',
            name='template_cache',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='bots.SentenceCache'),
        ),
    ]
