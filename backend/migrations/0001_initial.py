# Generated by Django 3.0.3 on 2020-04-14 12:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(default='', max_length=32, unique=True, verbose_name='公司名称')),
                ('quality', models.CharField(max_length=32, verbose_name='公司性质')),
                ('industry', models.CharField(max_length=32, verbose_name='公司所属行业')),
                ('scale', models.CharField(max_length=32, verbose_name='规模')),
                ('address', models.CharField(max_length=32, verbose_name='公司地址')),
                ('description', models.CharField(max_length=128, verbose_name='公司介绍')),
                ('status', models.CharField(default='0', max_length=1, verbose_name='状态')),
            ],
        ),
        migrations.CreateModel(
            name='Hunter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=32, verbose_name='姓名')),
                ('photo', models.ImageField(default='', upload_to='img', verbose_name='头像')),
                ('sex', models.CharField(default='0', max_length=1, verbose_name='性别')),
                ('birthday', models.DateField(default=django.utils.timezone.now, verbose_name='生日')),
                ('city', models.CharField(default='', max_length=10, verbose_name='所在城市')),
                ('Correspondence_address', models.CharField(default='', max_length=32, verbose_name='通讯地址')),
                ('registered_permanent_residence', models.CharField(default='', max_length=32, verbose_name='户口所在地')),
                ('education_background', models.CharField(default='本科', max_length=2, verbose_name='学历')),
                ('qq', models.CharField(default='', max_length=12, verbose_name='qq')),
            ],
        ),
        migrations.CreateModel(
            name='HunterPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_collect', models.CharField(default='0', max_length=1, verbose_name='是否收藏')),
                ('status', models.CharField(default='无', max_length=32, verbose_name='状态')),
                ('time', models.DateField(null=True, verbose_name='申请职位时间')),
                ('hunter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Hunter')),
            ],
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.DateField(null=True, verbose_name='申请职位时间')),
                ('title', models.CharField(max_length=20, verbose_name='标题')),
                ('content', models.CharField(max_length=200, verbose_name='内容')),
            ],
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('expected_work_city', models.CharField(default='', max_length=32, verbose_name='期望工作地点')),
                ('desired_position', models.CharField(default='', max_length=32, verbose_name='期望职位')),
                ('expected_salary', models.CharField(max_length=32, verbose_name='期望薪资')),
                ('self_assessment', models.CharField(default='', max_length=32, verbose_name='自我评价')),
                ('refresh_time', models.DateTimeField(auto_now=True)),
                ('hunter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Hunter')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_password', models.CharField(max_length=32)),
                ('user_type', models.CharField(default='1', max_length=1, verbose_name='用户类型')),
                ('user_email', models.EmailField(default='', max_length=254)),
                ('user_phone', models.CharField(default='', max_length=11)),
                ('creat_time', models.DateTimeField(auto_now_add=True)),
                ('last_login_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkExperience',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=32, verbose_name='公司名称')),
                ('entry_time', models.DateField(default=django.utils.timezone.now, verbose_name='入职时间')),
                ('dismission_time', models.DateField(default=django.utils.timezone.now, verbose_name='离职时间')),
                ('position_name', models.CharField(max_length=32, verbose_name='职位名称')),
                ('department', models.CharField(max_length=32, verbose_name='部门')),
                ('position_type', models.CharField(max_length=32, verbose_name='工作类型')),
                ('position_description', models.CharField(max_length=32, verbose_name='工作描述')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Resume')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectExperience',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project_name', models.CharField(max_length=32, verbose_name='项目名称')),
                ('start_time', models.DateField(default=django.utils.timezone.now, verbose_name='开始时间')),
                ('end_time', models.DateField(default=django.utils.timezone.now, verbose_name='结束时间')),
                ('project_description', models.CharField(max_length=32, verbose_name='项目描述')),
                ('institution', models.CharField(max_length=32, verbose_name='所属机构')),
                ('duty_description', models.CharField(max_length=32, verbose_name='责任描述')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Resume')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('position_name', models.CharField(max_length=32, verbose_name='职位名称')),
                ('release_time', models.DateField(auto_now_add=True, verbose_name='发布时间')),
                ('expiry_date', models.DateField(default=django.utils.timezone.now, verbose_name='过期时间')),
                ('workplace', models.CharField(max_length=32, verbose_name='工作地点')),
                ('pay', models.CharField(max_length=32, verbose_name='薪资')),
                ('count', models.IntegerField(default=0, verbose_name='人数')),
                ('sex', models.CharField(max_length=2, verbose_name='性别要求')),
                ('education_requirement', models.CharField(max_length=10, verbose_name='学历要求')),
                ('description', models.CharField(max_length=128, verbose_name='职位描述')),
                ('company_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Company', to_field='company_name')),
                ('hunters', models.ManyToManyField(through='backend.HunterPosition', to='backend.Hunter')),
            ],
        ),
        migrations.AddField(
            model_name='hunterposition',
            name='interview_id',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.Interview'),
        ),
        migrations.AddField(
            model_name='hunterposition',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Position'),
        ),
        migrations.AddField(
            model_name='hunter',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.User'),
        ),
        migrations.CreateModel(
            name='EducationExperience',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('school_name', models.CharField(max_length=32, verbose_name='学校名称')),
                ('enrollment_time', models.DateField(default=django.utils.timezone.now, verbose_name='入学时间')),
                ('graduation_time', models.DateField(default=django.utils.timezone.now, verbose_name='毕业时间')),
                ('education_background', models.CharField(max_length=32, verbose_name='学历')),
                ('major', models.CharField(max_length=32, verbose_name='专业')),
                ('honor', models.CharField(max_length=32, verbose_name='荣誉经历')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Resume')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.User'),
        ),
    ]