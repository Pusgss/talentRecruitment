# Generated by Django 2.2.12 on 2020-05-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_auto_20200502_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationexperience',
            name='honor',
            field=models.CharField(max_length=200, verbose_name='荣誉经历'),
        ),
        migrations.AlterField(
            model_name='position',
            name='description',
            field=models.CharField(max_length=200, verbose_name='职位描述'),
        ),
        migrations.AlterField(
            model_name='projectexperience',
            name='duty_description',
            field=models.CharField(max_length=200, verbose_name='责任描述'),
        ),
        migrations.AlterField(
            model_name='projectexperience',
            name='project_description',
            field=models.CharField(max_length=200, verbose_name='项目描述'),
        ),
        migrations.AlterField(
            model_name='workexperience',
            name='position_description',
            field=models.CharField(max_length=200, verbose_name='工作描述'),
        ),
    ]