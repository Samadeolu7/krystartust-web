# Generated by Django 5.1 on 2024-09-25 12:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liability', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='liability',
            old_name='amount',
            new_name='balance',
        ),
        migrations.AddField(
            model_name='liability',
            name='balance_bf',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='LiabilityPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('liability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='liability.liability')),
            ],
        ),
        migrations.DeleteModel(
            name='LiabilityRecord',
        ),
    ]