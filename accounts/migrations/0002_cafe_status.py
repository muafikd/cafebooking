# Generated by Django 5.0.6 on 2025-05-09 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='status',
            field=models.CharField(choices=[('active', 'Активно'), ('inactive', 'Неактивно')], default='active', max_length=10),
        ),
    ]
