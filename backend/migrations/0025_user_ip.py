# Generated by Django 2.2.12 on 2020-05-17 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0024_auto_20200514_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ip',
            field=models.CharField(default='', max_length=32),
        ),
    ]
