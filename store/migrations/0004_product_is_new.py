# Generated by Django 4.1.3 on 2022-12-05 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20221126_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_New',
            field=models.BooleanField(default=False),
        ),
    ]
