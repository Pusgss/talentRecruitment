# Generated by Django 2.2.12 on 2020-05-30 21:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0030_auto_20200530_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='release_time',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='发布时间'),
        ),
    ]
