# Generated by Django 4.0.4 on 2024-05-29 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0006_alter_playlist_created_alter_playlist_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='gender',
        ),
    ]
