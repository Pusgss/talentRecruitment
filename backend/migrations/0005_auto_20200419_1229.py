# Generated by Django 3.0.3 on 2020-04-19 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20200418_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyResume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_collect', models.CharField(default='0', max_length=1, verbose_name='是否收藏')),
                ('status', models.CharField(default='无', max_length=32, verbose_name='状态')),
                ('time', models.DateField(null=True, verbose_name='发送面试邀请时间')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Company')),
                ('interview_id', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.Interview')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Resume')),
            ],
        ),
        migrations.AddField(
            model_name='resume',
            name='companys',
            field=models.ManyToManyField(through='backend.CompanyResume', to='backend.Company'),
        ),
    ]
