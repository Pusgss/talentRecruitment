# Generated by Django 3.0.3 on 2020-04-25 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0014_auto_20200425_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(default='3', max_length=1, verbose_name='用户类型'),
        ),
    ]
