# Generated by Django 4.1.3 on 2022-12-16 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_product_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='mrp_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]