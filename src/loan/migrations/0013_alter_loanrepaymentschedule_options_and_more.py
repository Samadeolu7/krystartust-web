# Generated by Django 5.1.2 on 2024-11-29 11:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_monthstatus'),
        ('client', '0008_alter_client_client_id_alter_client_name'),
        ('loan', '0012_alter_loanpayment_payment_schedule'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loanrepaymentschedule',
            options={'ordering': ['due_date']},
        ),
        migrations.AddIndex(
            model_name='loanpayment',
            index=models.Index(fields=['loan', 'payment_date'], name='loan_loanpa_loan_id_853a35_idx'),
        ),
        migrations.AddIndex(
            model_name='loanpayment',
            index=models.Index(fields=['loan', 'payment_schedule'], name='loan_loanpa_loan_id_07a5db_idx'),
        ),
        migrations.AddIndex(
            model_name='loanpayment',
            index=models.Index(fields=['loan', 'created_at'], name='loan_loanpa_loan_id_15428c_idx'),
        ),
        migrations.AddIndex(
            model_name='loanrepaymentschedule',
            index=models.Index(fields=['loan', 'due_date', 'is_paid'], name='loan_loanre_loan_id_3b3909_idx'),
        ),
        migrations.AddIndex(
            model_name='loanrepaymentschedule',
            index=models.Index(fields=['loan', 'due_date', 'payment_date'], name='loan_loanre_loan_id_d8886d_idx'),
        ),
    ]