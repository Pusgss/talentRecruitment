# Generated by Django 2.2.12 on 2020-05-05 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0020_auto_20200505_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='self_assessment',
            field=models.CharField(default='', max_length=200, verbose_name='自我评价'),
        ),
    ]
