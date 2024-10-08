# Generated by Django 5.1 on 2024-09-25 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_alter_expense_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expense',
            old_name='duration',
            new_name='year',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='status',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='expense',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expensepayment',
            name='balance',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
