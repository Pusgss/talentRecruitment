# Generated by Django 3.0.3 on 2020-04-17 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_resume_resume_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='time',
            field=models.DateTimeField(null=True, verbose_name='申请职位时间'),
        ),
    ]
