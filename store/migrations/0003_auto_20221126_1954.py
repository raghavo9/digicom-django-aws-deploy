# Generated by Django 3.1 on 2022-11-26 19:54

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='variation',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
