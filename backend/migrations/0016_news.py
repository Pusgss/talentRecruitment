# Generated by Django 3.0.3 on 2020-04-28 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_auto_20200425_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(null=True, verbose_name='发表时间')),
                ('title', models.CharField(max_length=20, verbose_name='标题')),
                ('content', models.CharField(max_length=200, verbose_name='内容')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.User')),
            ],
        ),
    ]