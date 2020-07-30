from datetime import datetime

from django.db import models

# Create your models here.
#django orm不能帮你建库，但能建表
from django.utils import timezone

class User(models.Model):
    # user_type_choices=((1,'求职者'),(2,'企业'),(3,'管理员'))
    id =models.AutoField(primary_key=True)
    # MD5是最常见的摘要算法，速度很快，生成结果是固定的128    bit，通常用一个32位的16进制字符串表示。
    user_password=models.CharField(max_length=32)#实际6-20位，
    user_type=models.CharField(max_length=1,default='3',verbose_name='用户类型')#字符型
    user_email=models.EmailField(default="")#唯一，验证 ，登录时不能唯一unique=True,
    user_phone=models.CharField(max_length=11,default="")
    creat_time = models.DateTimeField(auto_now_add=True)  # 注册时间，第一次创建时间
    ip=models.CharField(max_length=32,default="")
    last_login_time=models.DateTimeField(auto_now=True)#最后登录时间
class Hunter(models.Model):
    user_name = models.CharField(max_length=32,verbose_name='姓名')
    photo = models.ImageField(upload_to='img', verbose_name="头像",default="")
    sex = models.CharField(max_length=1, verbose_name='性别',default="0")#bit
    birthday = models.DateField(default = timezone.now,verbose_name='生日')
    city = models.CharField(max_length=10, verbose_name='所在城市',default="")
    Correspondence_address = models.CharField(max_length=32, verbose_name='通讯地址',default="")
    registered_permanent_residence = models.CharField(max_length=32, verbose_name='户口所在地',default="")
    # education_backend_choices = (('大专', '大专'), ('本科', '本科'), ('硕士', '硕士'), ('博士', '博士'), ('其他', '其他'))
    education_background = models.CharField(max_length=2, verbose_name='学历',default="本科")
    # upload_to图片保存在该路径下, #上传的文件保存到MEDIA_root +upload_to后的路径
    qq = models.CharField(max_length=12, verbose_name='qq',default="")
    # 对于Django2.0版本，一对多（models.ForeignKey）和一对一（models.OneToOneField）要加上 on_delete=models.CASCADE 这个属性
    #null=True默认为空
    # 其中null = True是针对数据库的可以为空，而blank = True是针对表单验证validation的。如果blank = True没加，那么在下面做form的时候，省略字段的话验证不会通过。
    user = models.OneToOneField('User', on_delete=models.CASCADE)
   # resume也会被自动添加 _id
    #使用__str__方法帮助人性化显示对象信息；
    def __str__(self):
        return self.user_name
class Company(models.Model):
    # user_type_choices=((1,'求职者'),(2,'企业'),(3,'管理员'))
    id =models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=32,verbose_name='公司名称',default='',unique=True)
    quality=models.CharField(max_length=32,verbose_name='公司性质')
    industry=models.CharField(max_length=32,verbose_name='公司所属行业')
    scale=models.CharField(max_length=32,verbose_name='规模')
    address=models.CharField(max_length=32,verbose_name='公司地址')
    description=models.CharField(max_length=200,verbose_name='公司介绍')
    user = models.OneToOneField('User', on_delete=models.CASCADE)#外键
    status=models.CharField(max_length=1,verbose_name='状态',default='0')#0未审核，1已审核,2变更待审核,审核不通过直接删除

#简历
class Resume(models.Model):
    id=models.AutoField(primary_key=True)
    # sex_choices=(('m','男'),('f','女'))
    resume_name = models.CharField(max_length=32, verbose_name='简历名称')
    expected_work_city=models.CharField(max_length=32,verbose_name='期望工作地点',default="")
    desired_position=models.CharField(max_length=32,verbose_name='期望职位',default="")
    expected_salary=models.CharField(max_length=32,verbose_name='期望薪资')
    self_assessment=models.CharField(max_length=200,verbose_name='自我评价',default="")
    refresh_time=models.DateTimeField(auto_now=True)#更新时间、保存当前时间，不可修改
    temp=models.CharField(max_length=32,verbose_name='模板',default='temp1')
    hunter = models.ForeignKey('Hunter', on_delete=models.CASCADE)
    companys = models.ManyToManyField(Company, through='CompanyResume')
#教育经历
class EducationExperience(models.Model):
    id = models.AutoField(primary_key=True)
    school_name=models.CharField(max_length=32,verbose_name='学校名称')
    enrollment_time= models.DateField(default = timezone.now,verbose_name='入学时间')#可修改
    graduation_time= models.DateField(default = timezone.now,verbose_name='毕业时间')
    education_background=models.CharField(max_length=32,verbose_name='学历')
    major=models.CharField(max_length=32,verbose_name='专业')
    honor=models.CharField(max_length=200,verbose_name='荣誉经历')
    # 这句代码做了两件事：1. 生成表的时候在 publish前面自动加了 _id，并在表中生成了一个字段 publish_id；2. 把 publish_id 作为外键关联到了 Publish表的 nid 字段；
    resume=models.ForeignKey(to="Resume",to_field='id',on_delete=models.CASCADE)#简历删除，外键应数据也删除
#工作经历
class WorkExperience(models.Model):
    id = models.AutoField(primary_key=True)
    company_name=models.CharField(max_length=32,verbose_name='公司名称')
    entry_time= models.DateField(default = timezone.now,verbose_name='入职时间')
    dismission_time= models.DateField(default = timezone.now,verbose_name='离职时间')
    position_name=models.CharField(max_length=32,verbose_name='职位名称')
    department=models.CharField(max_length=32,verbose_name='部门')
    position_type=models.CharField(max_length=32,verbose_name='工作类型')
    position_description=models.CharField(max_length=200,verbose_name='工作描述')
    resume= models.ForeignKey(to="Resume", to_field='id', on_delete=models.CASCADE)  # 简历删除，外键应数据也删除

#项目经历
class ProjectExperience(models.Model):
    id = models.AutoField(primary_key=True)
    project_name=models.CharField(max_length=32,verbose_name='项目名称')
    start_time= models.DateField(default = timezone.now,verbose_name='开始时间')
    end_time= models.DateField(default = timezone.now,verbose_name='结束时间')
    project_description=models.CharField(max_length=200,verbose_name='项目描述')
    institution=models.CharField(max_length=32,verbose_name='所属机构')
    duty_description=models.CharField(max_length=200,verbose_name='责任描述')
    resume= models.ForeignKey(to="Resume", to_field='id', on_delete=models.CASCADE)  # 简历删除，外键应数据也删除


class Position(models.Model):
    id = models.AutoField(primary_key=True)
    position_name=models.CharField(max_length=32,verbose_name='职位名称')
    release_time=models.DateField(default = timezone.now,verbose_name='发布时间')#创建时间
    expiry_date = models.DateField(default = timezone.now, verbose_name='过期时间')
    workplace=models.CharField(max_length=32,verbose_name='工作地点')
    pay=models.CharField(max_length=32,verbose_name='薪资')#3000-3999
    count=models.IntegerField(default=0,verbose_name='人数')#若干,
    sex=models.CharField(max_length=2,verbose_name='性别要求')#男、女、不限
    education_requirement=models.CharField(max_length=10,verbose_name='学历要求')
    description=models.CharField(max_length=800,verbose_name='职位描述')
    company_name=models.ForeignKey(to="Company", to_field='company_name', on_delete=models.CASCADE)
    # company = models.ForeignKey(to="Company", to_field='id', on_delete=models.CASCADE)  # 简历删除，外键应数据也删除
    # 任职条件
    # 工作职责
    # 薪资待遇
    # 其他福利
    is_delete=models.CharField(max_length=1, verbose_name='qq',default="0")#是否删除0招聘，1企业停止招聘不能重新招聘2企业暂停招聘
    hunters=models.ManyToManyField(Hunter,through='HunterPosition')
class Interview(models.Model):
    id=models.AutoField(primary_key=True)
    time=models.DateTimeField(null=True, verbose_name='面试时间')
    title=models.CharField(max_length=20,verbose_name='标题')
    content=models.CharField(max_length=200,verbose_name='内容')
class HunterPosition(models.Model):
    hunter=models.ForeignKey(Hunter,on_delete=models.CASCADE)
    position=models.ForeignKey(Position,on_delete=models.CASCADE)
    resume=models.CharField(null=True,max_length=32,verbose_name='投递简历')#投递简历resume.id
    is_collect=models.CharField(default='0',max_length=1,verbose_name='是否收藏')#0,1
    status=models.CharField(default='无',max_length=32,verbose_name='状态')#3000-3999
    time=models.DateTimeField(null=True, verbose_name='申请职位时间')
    collect_time=models.DateField(null=True,verbose_name='收藏时间')
    interview=models.OneToOneField(Interview,on_delete=models.CASCADE,null=True)#面试邀请编号

class CompanyResume(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    resume=models.ForeignKey(Resume,on_delete=models.CASCADE)
    is_collect=models.CharField(default='0',max_length=1,verbose_name='是否收藏')#0,1
    status=models.CharField(default='无',max_length=32,verbose_name='状态')#3000-3999
    time=models.DateTimeField(null=True, verbose_name='发送面试邀请时间')
    collect_time=models.DateField(null=True,verbose_name='收藏时间')
    interview=models.OneToOneField(Interview,on_delete=models.CASCADE,null=True)#面试邀请编号

class News(models.Model):
    id=models.AutoField(primary_key=True)
    time=models.DateTimeField(null=True, verbose_name='发表时间')
    title=models.CharField(max_length=50,verbose_name='标题')
    content=models.CharField(max_length=1000,verbose_name='内容')
    user = models.ForeignKey(to="User", to_field='id', on_delete=models.CASCADE)  # 简历删除，外键应数据也删除



