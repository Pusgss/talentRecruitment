# Generated by Django 3.0.3 on 2020-04-21 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_auto_20200420_1844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyresume',
            old_name='interview_id',
            new_name='interview',
        ),
    ]