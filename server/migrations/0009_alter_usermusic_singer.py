# Generated by Django 4.0.4 on 2024-06-02 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_alter_usermusic_singer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermusic',
            name='singer',
            field=models.JSONField(),
        ),
    ]