# Generated by Django 5.1.2 on 2024-11-28 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0007_client_client_id_client_client_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='client_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]