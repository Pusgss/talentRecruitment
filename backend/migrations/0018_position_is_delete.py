# Generated by Django 3.0.5 on 2020-05-02 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_auto_20200429_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='is_delete',
            field=models.CharField(default='0', max_length=1, verbose_name='qq'),
        ),
    ]
