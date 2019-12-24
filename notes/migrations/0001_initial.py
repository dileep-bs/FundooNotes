# Generated by Django 2.2.6 on 2019-12-02 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=130)),
                ('datetime', models.CharField(max_length=60)),
                ('filename', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='name of label')),
                ('user', models.ForeignKey(default='admin', on_delete=django.db.models.deletion.CASCADE, related_name='label_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'label',
                'verbose_name_plural': 'labels',
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.URLField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500)),
                ('note', models.CharField(max_length=500)),
                ('image', models.ImageField(blank=True, max_length=500, null=True, upload_to='media')),
                ('is_archive', models.BooleanField(default=False, verbose_name='is_archived')),
                ('is_trashed', models.BooleanField(default=False, verbose_name='delete_note')),
                ('is_copied', models.BooleanField(default=False, verbose_name='make a copy')),
                ('checkbox', models.BooleanField(default=False, verbose_name='check box')),
                ('is_pined', models.BooleanField(default=False, verbose_name='is pinned')),
                ('url', models.URLField(blank=True, verbose_name='url')),
                ('reminder', models.DateTimeField(blank=True, null=True)),
                ('collaborators', models.ManyToManyField(blank=True, related_name='collaborators', to=settings.AUTH_USER_MODEL)),
                ('label', models.ManyToManyField(blank=True, related_name='label', to='notes.Label')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
        ),
    ]
