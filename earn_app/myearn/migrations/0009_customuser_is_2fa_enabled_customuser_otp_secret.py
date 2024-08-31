# Generated by Django 5.0.7 on 2024-08-30 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myearn', '0008_contactformsubmission'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_2fa_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_secret',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
