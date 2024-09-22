# Generated by Django 5.0.7 on 2024-09-11 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myearn', '0002_customuser_image_url_earninghistory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
