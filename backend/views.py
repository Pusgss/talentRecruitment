# -*- coding:utf-8 -*-
import datetime
import hashlib
import json
import os
import re
import uuid
import geoip2.database


import geoip2
from PIL import Image
from celery.task import periodic_task
from django.contrib.sites import requests
from django.core import serializers
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models, transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_list_or_404, redirect

# Create your views here.
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from pip._vendor.retrying import retry
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xhtml2pdf.default import DEFAULT_FONT

from backend import forms
from backend.forms import ModifyPwdForm
from backend.models import User, Resume, EducationExperience, WorkExperience, ProjectExperience, Hunter, Company, \
    Position, HunterPosition, CompanyResume, Interview, News
from talentRecruitment.settings import EMAIL_FROM
from random import Random, randint
from django.core.mail import send_mail

import logging
# 生成一个名为stu的logger实例，WARNING级别，写入log.txt文件
logger = logging.getLogger('stu')
loggerInfo = logging.getLogger('auth')

# python 函数make_password有相同功能
def get_md5(email,password):
    md5=hashlib.md5()
    md5.update(str(password+email).encode('utf-8'))
    return md5.hexdigest()

# 发送五位码到邮箱，并存入redis
def send_email(request):
    if request.method=='POST':
        try:
            #修改密码
            if request.session.get('is_login', None):#已登录
                id=request.session.get('user_id')
                user=User.objects.filter(id=id).first
                email=user.user_email
            # 注册
            else:
                email = request.POST.get('user_email')
            # 生成随机的验证码
            code = email_code()
            ret = '您好，\n您正在请求绑定邮箱，请在5分钟内输入一下验证码完成绑定。如非本人造作，请忽略此邮件\n您的验证码是{}'.format(code)
            # 给邮箱发送验证码
            status =send_mail('激活验证', ret, EMAIL_FROM, [email],fail_silently=False)
            status=1
            if not status == 1:
                return JsonResponse({
                    'code': 0,
                    'msg': "邮件发送失败,请检查邮箱是否正确",
                })
            key = 'syl_' + email
            # 保存到redis,键值有效时间
            cache.set(key, code, 300)  # 5分钟的有效时间
            print(code)
            return JsonResponse({
                'code': 200,
                'msg': "邮件发送成功"
            })
        # 返回错误信息
        except Exception as e:
            logger.warning(f'{e}')
            return JsonResponse({'code': 0, 'msg': '网络超时，获取验证码失败！'})

# 生成随机5位字符串验证码
def email_code():
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"
    length=len(chars)
    code=''
    for i in range(5):
        code+=chars[randint(0,length)]
    return code
# @require_http_methods(["GET"])
# def add_user(request):
#     response={}
#     try:
#         user=User(user_name=request.GET.get('user_name'),user_password=request.GET.get('user_password'))
#         user.save()
#         response['msg']='success'
#         response['error_num']=0
#     except Exception as e:
#         response['msg']=str(e)
#         response['error_num']=1
#     return JsonResponse(response)
#求职者首页
def index(request):
    # return HttpResponse("Hello,world.You are at the backend index")
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    return render(request, 'backend/hunter/index.html')

#request.META获取ip
def get_ip(request):
    """获取访问页面及客户端ip地址"""
    ip = None
    proxy_ip = None
    server_name = request.META.get('SERVER_NAME')
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        proxy_ip = request.META.get("REMOTE_ADDR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    # # 获取物理地址
    # if not ip=="127.0.0.1":  # 本地测试忽略
    #     try:
    #         address = ip_to_addr(ip)
    #
    #     except Exception as e:
    #         print(e)
    #         address = '获取失败'
    return ip

#ip转为物理地址
# def ip_to_addr(ip):
#     """
#     IP 转换成现实中的地理位置
#     country = 国家
#     province = 省
#     city = 城市
#     """
#     reader = geoip2.database.Reader('backend/GeoLite2-City.mmdb')
#     # response = reader.city('119.115.204.245')
#     response = reader.city('112.74.207.96')
#
#     # print(response)
#     # 因为有些IP的省份和城市未知，所以设置默认为空
#     province = ''
#     city = ''
#     try:
#         # 国家、省份、城市
#         country = response.country.names["zh-CN"]
#         province = response.subdivisions.most_specific.names["zh-CN"]
#         city = response.city.names["zh-CN"]
#         print('province'+province)
#         print(city)
#     except Exception as e:
#         print(e)
#     if country != '中国':
#         return country
#     if province and city:
#         if province == city or city in province:
#             return province
#         return '%s%s' % (province, city)
#     elif province and not city:
#         return province
#     else:
#         return country



#Django内置的视图装饰器
# @require_http_methods(["POST"])
def login(request):
    if request.session.get('is_login',None):#不允许重复登录
        user_type=request.session.get('user_type')
        if user_type=='1':
            return redirect('/api/index/')
        elif user_type=='2':
            return redirect('/api/company_index/')
        elif user_type=='3':
            return redirect('/api/admin_index/')
    if request.method=='POST':
        #request.POST封装了所有POST请求中的数据
        # user_name = request.POST.get('user_name')
        # user_password = request.POST.get('user_password')
        login_form=forms.LoginForm(request.POST)
        ret = {'status': 'successful', 'errs': None}
        if login_form.is_valid():
            user_email=login_form.cleaned_data.get('user_email')
            user_password=login_form.cleaned_data.get('user_password')
            try:
                user=User.objects.get(user_email=user_email)
            except Exception as e:
                message='用户不存在！'
                ret['status'] = 'warning'
                ret['errs'] =message
                return HttpResponse(json.dumps(ret))
            # 登录成功
            if user.user_password==get_md5(user_email,user_password):
                request.session['user_id']=user.id
                request.session['user_type'] = user.user_type
                #企业审核状态
                if user.user_type=='2':
                    company=Company.objects.filter(user_id=user.id).first()
                    if company.status=='0':
                        message = "请耐心等待审核通过！"
                        ret['status'] = "warning"
                        ret['errs'] = message
                        return HttpResponse(json.dumps(ret))
                    #企业已通过审核
                    else:
                        request.session['user_name']=company.company_name
                        request.session['is_login'] = True
                # 求职者直接登录
                elif user.user_type=='1':
                    request.session['is_login'] = True
                    request.session['user_name'] =Hunter.objects.filter(user_id=user.id).first().user_name
                # 管理员直接登录
                else:
                    request.session['is_login'] = True
                # 获取ip
                ip=get_ip(request)
                user.ip=ip
                request.session['ip'] = ip
                request.session['user_email'] = user_email
                # 更新最后登录时间
                user.save()
                # 登录信息写入日志文件
                loggerInfo.info(f'{user_email} {ip} --login in ')

                ret['user_type']=user.user_type
                return HttpResponse(json.dumps(ret))
            #密码错误
            else:
                message="密码不正确！"
                ret['status'] = "warning"
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
        #表单验证失败
        else:
            error = login_form.errors
            ret['status'] = "fail"
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
    #请求页面
    login_form=forms.LoginForm()
    return render(request,'backend/login.html',locals())


def register(request):
    #已登录
    if request.session.get('is_login',None):
        user_type = request.session.get('user_type')
        if user_type == '1':
            return redirect('/api/index/')
        elif user_type == '2':
            return redirect('/api/company_index/')
        else:
            return redirect('/api/admin_index/')
    #注册
    if request.method=='POST':
        #获取表单输入
        register_form=forms.RegisterForm(request.POST)
        ret = {'status': 'successful', 'errs': None}
        if register_form.is_valid():
            user_password=register_form.cleaned_data.get('user_password')
            user_type=register_form.cleaned_data.get('user_type')
            user_email=register_form.cleaned_data.get('user_email')
            code = request.POST.get('code')
            #邮箱是否已注册
            same_user_email = User.objects.filter(user_email=user_email)
            if same_user_email:
                message='该邮箱已被注册了'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            # same_user_phone = User.objects.filter(user_phone=user_phone)
            # if same_user_phone:
            #     message = '该手机号已被注册了'
            #     ret['status'] = 'warning'
            #     ret['errs'] = message
            #     return HttpResponse(json.dumps(ret))
            if not code:
                message='请输入验证码'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            code_ = cache.get('syl_' + user_email)
            if not code_:
                message = '验证码已失效'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            if code == code_:
                pass
            else:
                message = '验证码错误'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            register_form=register_form.save(commit=False)
            register_form.user_password=get_md5(user_email,user_password)
            register_form.save()
            id = register_form.id
            request.session['user_id'] = id
            if user_type=="1":
                #求职者注册完成便登陆
                request.session['is_login'] = True
            #前端根据用户类型跳转到信息填写界面
            ret['user_type'] = user_type
            return HttpResponse(json.dumps(ret))
        #表单验证失效
        else:
            error = register_form.errors
            ret['status'] = "fail"
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))


#登出
def logout(request):
    #未登录
    if not request.session.get('is_login',None):
        return redirect('/api/login/')
    user_email=request.session.get('user_email')
    ip = request.session.get('ip')
    loggerInfo.info(f'{user_email} {ip} --login out')
    #清理
    request.session.flush()
    #页面重定向
    return redirect('/api/login/')


#更改密码：验证码与密码一致
def update_pwd(request):
    if request.method=="POST":
        ret = {'status': 'successful', 'errs': None}
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('user_password', '')  # 与html中name值一样
            pwd2 = request.POST.get('password2', '')
            code = request.POST.get('code')
            user_email = request.POST.get('user_email')
            if not code:
                message='请输入验证码'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            code_ = cache.get('syl_' + user_email)
            if not code_:
                message = '验证码已失效'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            if code == code_:
                pass
            else:
                message = '验证码错误'
                ret['status'] = 'warning'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            if pwd1 != pwd2:
                message = '两次密码不一致'
                ret['status'] = 'waring'
                ret['errs'] = message
                return HttpResponse(json.dumps(ret))
            # 密码加密保存
            # user_id = request.session.get('user_id')
            user = User.objects.filter(user_email=user_email).first()
            user.password = get_md5(user.user_email,pwd1)
            user.save()
            message = '修改成功'
            ret['status'] = 'successful'
            ret['errs'] = message
            return HttpResponse(json.dumps(ret))
        else:
            error = modify_form.errors
            ret['status'] = "fail"
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
    else:
        return render(request,'backend/update_pwd.html',locals())


# @require_http_methods(["POST"])
# def user_detail(request,id):
#
#     user=User.objects.filter(id=id)
#     form =forms.RegisterForm(instance=user)
#     return  render(request,'backend/user_detail',locals())删除用户
@require_http_methods(['POST'])
def user_del(request):
    # user=User.objects.filter(id=id)
    # user.delete()
    # return redirect('/api/show_users')
    if request.method == "POST":
            userid = request.POST.get('userid')
            status = "删除成功！"
            result = "Error!"
            deletesql = User.objects.filter(id=userid)  # 执行删除操作
            if deletesql.delete():
                return HttpResponse(json.dumps({
                    'status': status
                }))
            else:
                return HttpResponse(json.dumps({
                   'result': result
                }))
#求职者注册后完善个人信息
def hunter_add(request):
    if request.method=='POST':
        hunter_form = forms.HunterForm(request.POST)
        user_id=request.session.get('user_id')
        print(user_id)
        if hunter_form.is_valid():
            hunter_form=hunter_form.save(commit=False)
            hunter_form.user_id=user_id
            hunter_form.save()
            request.session['user_name'] = hunter_form.user_name
            return JsonResponse({'status':'successful'})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = hunter_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
    else:
        return render(request, 'backend/hunter/hunterForm.html')

def user_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='GET':
        user=User.objects.filter(id=id).first()
        # 创建一个表单，并用instance = article当前数据填充表单
        user_form = forms.UserForm(instance=user)
        return render(request,'backend/user_edit.html',locals())

    else:
        user = User.objects.filter(id=id).first()
        hunter=Hunter.objects.filter(user=user.id).first()
        # instance = article当前数据填充表单指定这次修改的对象，并用data = request.POST获取到表单里的内容
        user_form = forms.UserForm(instance=user, data=request.POST)
        hunter_form = forms.HunterForm(instance=hunter, data=request.POST)
        # 如果 instance 有对象则是修改数据 没有就是 新增数据，进行保存
        if user_form.is_valid()& hunter_form.is_valid():  # 验证
            user_form.save()  # 保存
            hunter_form.save()  # 保存
            return JsonResponse({'status': "successful"})
        elif not user_form.is_valid():
            ret = {'status': 'successful', 'errs': None
                   }
            error = user_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
        else:
            ret = {'status': 'successful', 'errs': None
                   }
            error = hunter_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
            # user_phone=request.POST.get('user_phone')
            # user_password=request.POST.get('user_password')
            # user_email=request.POST.get('user_email')
            # User.objects.filter(id=id).update(user_phone=user_phone, user_password=user_password,user_email=user_email)
            # return redirect('/api/show_users')


#保存图片到用户文件夹下，并返回图片路径
def crop_image(file,id):
    # *************路径保存到数据库*******************************
    # 获取文件后缀
    ext=file.name.split('.')[-1]
    #uuid随机数的uuid，通用唯一标识码（36个字符10进制），hex10进制转为16进制
    file_name='{}.{}'.format(uuid.uuid4().hex[:10],ext)
    #路径拼接：用户id\photo\文件名
    #cropped_photo上传到数据库的文件路径
    cropped_photo=os.path.join(str(id),'photo',file_name)


    #*************保存到项目文件夹下*******************************
    # 相对根目录路径
    file_path = os.path.join("media", str(id), "photo")
    #创建文件夹，将图图片保存到文件下
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path1= os.path.join(file_path,file_name)
     # 裁剪图片,压缩尺寸为200*200。
    img = Image.open(file)
    if img.mode == "P":
        img = img.convert('RGB')
    img.save(file_path1)
    return cropped_photo

#创建简历（最多三份）
def resume_add(request):
    if request.method=='POST':
        user_id = request.session.get('user_id')
        hunter = Hunter.objects.filter(user_id=user_id).first()
        resume_list=Resume.objects.filter(hunter_id=hunter.id)
        ret = {'status': 'successful', 'errs': None}
        if resume_list.count()>3:
            ret['status'] = 'warning'
            ret['errs'] = '最多可创建三份简历'
            return HttpResponse(json.dumps(ret))
        # instance = article当前数据填充表单指定这次修改的对象，并用data = request.POST获取到表单里的内容
        resume_form = forms.ResumeForm(data=request.POST)
        # 如果 instance 有对象则是修改数据 没有就是 新增数据，进行保存
        if resume_form.is_valid():  # 验证
            form = resume_form.save(commit=False)
            form.hunter_id=hunter.id
            form.save()
            # 提交数据库
            return JsonResponse(ret)
        else:
            error = resume_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))



#简历编辑
def resume_edit(request,id):
    if request.method=='POST':
        resume = Resume.objects.filter(id=id).first()
        # instance = article当前数据填充表单指定这次修改的对象，并用data = request.POST获取到表单里的内容
        resume_form = forms.ResumeForm(instance=resume, data=request.POST)
        # 如果 instance 有对象则是修改数据 没有就是 新增数据，进行保存
        if resume_form.is_valid():  # 验证
            form = resume_form.save(commit=False)
            # 提交数据库
            form.save()
            return JsonResponse({'status': "successful"})
        else:
            ret = {'status': 'successful', 'errs': None
                   }
            error = resume_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

#简历中心
def resumeCenter(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if  request.method=='POST':
        user = User.objects.filter(id=request.session.get('user_id')).first()
        hunter = Hunter.objects.filter(user_id=user.id).first()
        resumes= Resume.objects.filter(hunter_id=hunter.id)
        if resumes:
            resume_list = serializers.serialize('json', resumes)
        #获取简历被邀请数量
        interviewCount = []
        count=[]
        for resume in resumes:
            hunterPositions = HunterPosition.objects.filter(status='interview', resume=resume.id)
            companyResumes = CompanyResume.objects.filter(status='interview', resume_id=resume.id)
            interviewCount.append(hunterPositions.count() + companyResumes.count())
        #简历被浏览次数，企业操作会更新浏览次数
        for resume in resumes:
            hunterPositions = HunterPosition.objects.filter(status__in=['interview','checked','improper'], resume=resume.id)
            companyResumes = CompanyResume.objects.filter(status__in=['interview','checked','improper'], resume_id=resume.id)
            count.append(hunterPositions.count() + companyResumes.count())
        return JsonResponse({'resume_list': resume_list,'interviewCount':interviewCount,'count':count})
    # 请求页面
    else:
        return render(request, 'backend/hunter/resumCenter.html')

#求职者照片上传
@csrf_exempt
def photoUpload(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        hunter = Hunter.objects.filter(user_id=user_id).first()
        img = request.FILES['file'] # 获取上传图片
        cropped_photo = crop_image(img, user_id)
        hunter.photo = cropped_photo# 将图片路径修改到当前会员数据库
        hunter.save()
        return JsonResponse({'status': "successful"})

# 教育背景添加
def education_experience_add(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        education_form = forms.EducationExperienceForm(request.POST)
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(user_id=user_id).first()
        if education_form.is_valid():
            education_form=education_form.save(commit=False)
            education_form.resume_id=request.session.get('resume_id')
            resume=Resume.objects.filter(id=request.session.get('resume_id')).first()
            resume.refresh_time=timezone.now()
            resume.save()
            education_form.save()
            education_experience_list=[]
            education_experience=EducationExperience.objects.last()
            education_experience_list.append(education_experience)
            education_experience_list=serializers.serialize('json',education_experience_list)
            return JsonResponse({'status':'successful','education_experience':education_experience_list})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = education_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
# 教育背景修改
def education_experience_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        education_experience=EducationExperience.objects.filter(id=id).first()
        education_experience_form = forms.EducationExperienceForm(request.POST,instance=education_experience)
        if education_experience_form.is_valid():
            education_experience_form.save()
            resume = Resume.objects.filter(id=education_experience.resume_id).first()
            #修改简历更新时间
            resume.refresh_time = timezone.now()
            resume.save()
            return JsonResponse({'status': "successful"})
        else:
            ret={'status':'successful','errs':None
                 }
            error = education_experience_form.errors
            ret['status']='fail'
            ret['errs']=error.as_json()
            return HttpResponse(json.dumps(ret))

# 教育背景删除
def education_experience_del(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        education_experience = EducationExperience.objects.filter(id=id).first()
        if education_experience.delete():
            print('cheng')
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })

def work_experience_add(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        work_form = forms.WorkExperienceForm(request.POST)
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(user_id=user_id).first()
        if work_form.is_valid():
            work_form=work_form.save(commit=False)
            resume_id = request.session.get('resume_id')
            work_form.resume_id=resume_id
            resume = Resume.objects.filter(id=request.session.get('resume_id')).first()
            resume.refresh_time = timezone.now()
            resume.save()
            work_form.save()
            work_experience_list=[]
            work_experience=WorkExperience.objects.last()
            work_experience_list.append(work_experience)
            work_experience_list=serializers.serialize('json',work_experience_list)
            return JsonResponse({'status':'successful','work_experience':work_experience_list})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = work_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            print(json.dumps(ret))
            return HttpResponse(json.dumps(ret))

def work_experience_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        work_experience=WorkExperience.objects.filter(id=id).first()
        work_form = forms.WorkExperienceForm(request.POST,instance=work_experience)
        if work_form.is_valid():
            resume = Resume.objects.filter(id=work_experience.resume_id).first()
            resume.refresh_time = timezone.now()
            resume.save()
            work_form.save()
            return JsonResponse({'status': "successful"})
        else:
            ret={'status':'successful','errs':None
                 }
            error = work_form.errors
            ret['status']='fail'
            ret['errs']=error.as_json()
            print(json.dumps(ret))
            return HttpResponse(json.dumps(ret))


def work_experience_del(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        work_experience = WorkExperience.objects.filter(id=id).first()
        if work_experience.delete():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })

def project_experience_add(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        project_form = forms.ProjectExperienceForm(request.POST)
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(id=user_id).first()
        if project_form.is_valid():
            project_form=project_form.save(commit=False)
            project_form.resume_id=request.session.get('resume_id')
            resume = Resume.objects.filter(id=request.session.get('resume_id')).first()
            resume.refresh_time = timezone.now()
            resume.save()
            project_form.save()
            project_experience_list=[]
            project_experience=WorkExperience.objects.last()
            project_experience_list.append(project_experience)
            project_experience_list=serializers.serialize('json',project_experience_list)
            return JsonResponse({'status':'successful','project_experience':project_experience_list})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = project_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()

            return HttpResponse(json.dumps(ret))

def project_experience_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        project_experience=ProjectExperience.objects.filter(id=id).first()
        project_form = forms.WorkExperienceForm(request.POST,instance=project_experience)
        if project_form.is_valid():
            resume = Resume.objects.filter(id=project_experience.resume_id).first()
            resume.refresh_time = timezone.now()
            resume.save()
            project_form.save()
            return JsonResponse({'status': "successful"})
        else:
            ret={'status':'successful','errs':None
                 }
            error = project_form.errors
            ret['status']='fail'
            ret['errs']=error.as_json()
            print(json.dumps(ret))
            return HttpResponse(json.dumps(ret))


def project_experience_del(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        project_experience =ProjectExperience.objects.filter(id=id).first()
        if project_experience.delete():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })

#求职者查看自己的每份简历：session['id']
def resume_show(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if  request.method=='POST':
        resume_id=request.session.get('resume_id')
        user_list=[]
        hunter_list = []
        resume_list=[]
        user = User.objects.filter(id=request.session.get('user_id')).first()
        hunter = Hunter.objects.filter(user=user).first()
        user_list.append(user)
        hunter_list.append(hunter)
        user_list = serializers.serialize('json', user_list)
        hunter_list = serializers.serialize('json', hunter_list)
        resume = Resume.objects.filter(id=resume_id,hunter_id=hunter.id).first()
        #编辑
        if resume:
            resume_list.append(resume)
            resume_list = serializers.serialize('json', resume_list)
            # resume_form=forms.ResumeForm(instance=resume)
            education_experience_list=EducationExperience.objects.filter(resume_id=resume.id)
            work_experience_list=WorkExperience.objects.filter(resume_id=resume.id)
            project_experience_list=ProjectExperience.objects.filter(resume_id=resume.id)
            # if education_experience_list:
            education_experience_list = serializers.serialize('json', education_experience_list)
            #     education_experience_form_list=[]
            #     for education_experience in education_experience_list:
            #         education_experience_form = forms.EducationExperienceForm(instance=education_experience)
            #         # print(education_experience_form.cleaned_data['id'])
            #         education_experience_form_list.append(education_experience_form)
            #     zip1=zip(education_experience_list,education_experience_list)
            # if work_experience_list:
            work_experience_list = serializers.serialize('json', work_experience_list)
            #     work_experience_form_list = []
            #     for work_experience in work_experience_list:
            #         work_experience_form = forms.WorkExperienceForm(instance=work_experience)
            #         work_experience_form_list.append(work_experience_form)
            #
            # if project_experience_list:
            project_experience_list = serializers.serialize('json', project_experience_list)
            #     project_experience_form_list = []
            #     for project_experience in project_experience_list:
            #         project_experience_form = forms.ProjectExperienceForm(instance=project_experience)
            #         project_experience_form_list.append(project_experience_form)
        # return render(request, 'backend/resume_show.html', locals())
            return JsonResponse({'user_list':user_list,'hunter_list':hunter_list,'resume_list':resume_list,'education_experience_list': education_experience_list,'work_experience_list':work_experience_list,'project_experience_list':project_experience_list})
        return JsonResponse({'user_list':user_list,'hunter_list':hunter_list})
    # 请求页面
    else:
        resume_id = request.GET.get('id')
        request.session['resume_id']=resume_id
        return render(request, 'backend/hunter/resume_show.html')

#求职者删除简历
def resumeCenterDelete(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position_id_list = request.POST.get('id_list')
        position_id_list = position_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        ret = {'status': 'successful', 'errs': None}
        print(position_id_list)
        for i in position_id_list:
            resume =Resume.objects.filter(id=i).first()
            if resume.delete():
               pass
            else:
                ret['status']='warning'
                ret['errs']='删除失败'
                return JsonResponse(ret)
        return JsonResponse(ret)

#求职者删除简历(前端保证至少有一份简历)已不用
def resume_del(request,id):
    if request.method=='GET':
        resume=Resume.objects.filter(id=id).first()
        resume.delete()
        return redirect('/api/reusme_show')
#
# #修改教育背景等
# def BookEdit(request,id):
#     if not request.session.get('is_login', None):
#         return redirect('/api/login/')
#     education_experience = EducationExperience.objects.filter(id=id).first()
#     #获取修改数据的表单
#     if request.method == "GET":
#         form = forms.EducationExperienceForm(instance=education_experience)
#         return render(request, 'booklist.html', locals())
#     #POST请求添加修改过后的数据
#     form = forms.EducationExperienceForm(data=request.POST,instance=education_experience)
#     #对数据验证并且保存
#     if form.is_valid():
#         form.save()
#         return redirect('/api/resume_show')

#获取求职者简历投递反馈数量
def getFeedbackCount(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id = request.session.get('user_id')
        hunter = Hunter.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        deliverCount=0
        checkedCount = 0
        interviewCount = 0
        improperCount = 0
        count=[]
        hunterPositions = HunterPosition.objects.filter(hunter_id=hunter.id)
        if hunterPositions:
            for j in hunterPositions:
                print(j.status)
                if j.status == 'improper':
                    improperCount=improperCount+1
                elif j.status == 'deliver':
                    deliverCount = deliverCount + 1
                elif j.status == 'checked':
                    checkedCount = checkedCount + 1
                elif j.status == 'interview':
                    interviewCount = interviewCount + 1
        count.append(deliverCount)
        count.append(checkedCount)
        count.append(interviewCount)
        count.append(improperCount)
        ret['count']=count
        return JsonResponse(ret)

#求职者查看所有职位信息，发布时间排名
def allPositionSearch(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')#当前页
        pageSize = int(request.POST.get('pageSize'))#每页个数
        company_list=[]
        position_list = Position.objects.filter(is_delete='0').order_by("-release_time")
        paginator = Paginator(position_list, pageSize)
        try:
            positions = paginator.page(page)
        except PageNotAnInteger:
            positions = paginator.page(1)
        except EmptyPage:
            #分页数，最后一页
            positions = paginator.page(paginator.num_pages)
        for position in positions:
            company_list.append(Company.objects.filter(company_name=position.company_name_id).first())
        company_list = serializers.serialize('json', company_list)
        position_list = serializers.serialize('json', positions)
        return JsonResponse({'status': 'successful', 'position_list': position_list,'total':paginator.count})
    else:
        return render(request, 'backend/hunter/all_position_search.html')

#求职者关键字查询职位
def positionSearch(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        category=request.POST.get('category')#类别
        keyword=request.POST.get('keyword')#关键字
        position_list=[]
        if  category=='position_name':
            position_list=Position.objects.filter(position_name=keyword,is_delete='0').order_by("-release_time")
        elif category=='workplace':
            position_list = Position.objects.filter(workplace=keyword,is_delete='0').order_by("-release_time")
        paginator = Paginator(position_list, pageSize)
        count = paginator.count#总数量
        try:
            positions = paginator.page(page)
        except PageNotAnInteger:
            positions = paginator.page(1)
        except EmptyPage:
            positions = paginator.page(paginator.num_pages)
        position_list = serializers.serialize('json', positions)
        return JsonResponse({'status': 'successful', 'position_list': position_list,'total':count})

#求职者收藏职位
def positionCollect(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position_id_list = request.POST.get('id_list')
        position_id_list = position_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(user_id=user_id).first()
        # hunter=[]
        ret = {'status': 'successful', 'errs': None}
        try:
            for i in position_id_list:
                 hunterPosition=HunterPosition.objects.filter(hunter_id=hunter.id,position_id=i).first()
                 if hunterPosition:
                     # 未收藏
                     if hunterPosition.is_collect=='0':
                         hunterPosition.is_collect='1'
                         hunterPosition.collect_time=timezone.now()
                         hunterPosition.save()
                     else:
                        pass
                     # message = '您已收藏！'
                     # ret['status'] = 'warning'
                     # ret['errs'] = message
                     # return JsonResponse(ret)
                 else:
                    position=Position.objects.get(id=i,is_delete='0')
                    hunterPosition=HunterPosition(hunter=hunter,position=position,is_collect='1',collect_time=timezone.now())
                    hunterPosition.save()
            return JsonResponse({'status': 'successful'})
        except Exception as e:
            # logger.error('error message')
            logger.warning(f'{e}')
            ret['status']='warning'
            ret['errs']=e
            return JsonResponse(ret)


# 求职者关键字查询职位
def resumeSearch(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        category = request.POST.get('category')
        keyword = request.POST.get('keyword')
        print(category)
        hunter_list = []
        resume_list = []
        user_list = []
        if category == 'sex':
            if keyword == '女':
                keyword = '1'
            elif keyword == '男':
                keyword = '0'
            hunters = Hunter.objects.filter(sex=keyword)
            for hunter in hunters:
                resume = Resume.objects.filter(hunter_id=hunter.id).first()
                resume_list.append(resume)
            # resume_list=resume_list.order_by('-refresh_time')
            # 逆序
            resume_list.sort(key=lambda t: t.refresh_time, reverse=True)

            paginator = Paginator(resume_list, pageSize)
            count = paginator.count
            try:
                resume_list = paginator.page(page)
            except PageNotAnInteger:
                resume_list = paginator.page(1)
            except EmptyPage:
                resume_list = paginator.page(paginator.num_pages)
            for i in resume_list:
                hunter = Hunter.objects.filter(id=i.hunter_id).first()
                hunter_list.append(hunter)
                user = User.objects.filter(id=hunter.user_id).first()
                user_list.append(user)
        elif category == 'education_background':
            hunters = Hunter.objects.filter(education_background=keyword)
            for hunter in hunters:
                resume = Resume.objects.filter(hunter_id=hunter.id).first()
                resume_list.append(resume)
            # list根据更新时间进行排序
            resume_list.sort(key=lambda t: t.refresh_time, reverse=True)
            paginator = Paginator(resume_list, pageSize)
            count = paginator.count
            try:
                resume_list = paginator.page(page)
            except PageNotAnInteger:
                resume_list = paginator.page(1)
            except EmptyPage:
                resume_list = paginator.page(paginator.num_pages)
            for i in resume_list:
                hunter = Hunter.objects.filter(id=i.hunter_id).first()
                hunter_list.append(hunter)
                user = User.objects.filter(id=hunter.user_id).first()
                user_list.append(user)
        elif category == 'desired_position':
            resume_list = Resume.objects.filter(desired_position=keyword).order_by('-refresh_time')
            paginator = Paginator(resume_list, pageSize)
            count = paginator.count
            try:
                resume_list = paginator.page(page)
            except PageNotAnInteger:
                resume_list = paginator.page(1)
            except EmptyPage:
                resume_list = paginator.page(paginator.num_pages)

            for i in resume_list:
                hunter = Hunter.objects.filter(id=i.id).first()
                hunter_list.append(hunter)
                user = User.objects.filter(id=hunter.user_id).first()
                user_list.append(user)
        resume_list = serializers.serialize('json', resume_list)
        user_list = serializers.serialize('json', user_list)
        hunter_list = serializers.serialize('json', hunter_list)
        return JsonResponse(
            {'status': 'successful', 'user_list': user_list, 'resume_list': resume_list, 'hunter_list': hunter_list,
             'total': count})


#求职者申请职位
def positionDeliver(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position_id_list=request.POST.get('id_list')
        resume_id = request.POST.get('resume_id')
        position_id_list=position_id_list.replace('[','').replace(']','').strip('\'').split(',')
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        try:
            for i in position_id_list:
                hunterPosition=HunterPosition.objects.filter(hunter_id=hunter.id,position_id=i).first()
                if hunterPosition:
                    #未申请过
                    if hunterPosition.status=="无":
                        hunterPosition.status='deliver'
                        hunterPosition.time=timezone.now()#申请职位时间
                        hunterPosition.resume=resume_id
                        hunterPosition.save()
                        # return JsonResponse(ret)
                    # 申请过但企业未处理，更新简历
                    elif hunterPosition.status=="deliver":
                        # 更新投递的简历
                        # pass
                        hunterPosition.resume = resume_id
                        hunterPosition.save()
                    # 企业已处理
                    else:
                        message = '您已申请过该职位！'
                        ret['status'] = 'warning'
                        ret['errs'] = message
                    #     return JsonResponse(ret)
                else:
                    position=Position.objects.get(id=i,is_delete='0')
                    hunterPosition=HunterPosition(hunter=hunter,position=position,status='deliver',
                                                  resume=resume_id,time=timezone.now())
                    hunterPosition.save()
            return JsonResponse(ret)
        except Exception as e:
            ret['errs']=e
            ret['status'] = 'warning'
            logger.info(f'{e}')
            return JsonResponse(ret)

#我的投递:申请、不合适、面试邀请
def myDeliver(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        #投递状态
        status=request.POST.get('activeName')
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(user_id=user_id).first()
        hunterPositions=HunterPosition.objects.filter(hunter_id=hunter.id)
        position_list=[]
        interview_list=[]
        company_list=[]
        hunter_position_list=[]
        company_resume_list=[]
        resume_list=[]
        for hunterPosition in hunterPositions:
            if hunterPosition.status==status:
                hunter_position_list.append(hunterPosition)
                resume=Resume.objects.filter(id=hunterPosition.resume).first()
                if resume:
                    resume_list.append(resume)
                else:
                    resume = Resume()
                    resume.resume_name = '简历已被删除'
                    resume_list.append(resume)
                position=Position.objects.filter(id=hunterPosition.position_id).first()
                company_list.append(Company.objects.filter(company_name=position.company_name_id).first())
                position_list.append(position)
                if status == 'interview':
                    interview_list.append(Interview.objects.filter(id=hunterPosition.interview_id).first())
        if status == 'interview':
            resumes=Resume.objects.filter(hunter_id=hunter.id)
            for resume in resumes:
                companyResumes = CompanyResume.objects.filter(resume_id=resume.id)
                if companyResumes:
                    for j in companyResumes:
                        if j.status == status:
                            company_resume_list.append(j)
                            # position_list.append(Position.objects.filter(id=j.position_id, is_delete='0').first())
                            company_list.append(Company.objects.filter(id=j.company_id).first())
                            interview_list.append(Interview.objects.filter(id=j.interview_id).first())
        company_resume_list=serializers.serialize('json', company_resume_list)
        company_list = serializers.serialize('json', company_list)
        position_list = serializers.serialize('json', position_list)
        interview_list = serializers.serialize('json', interview_list)
        hunter_position_list= serializers.serialize('json', hunter_position_list)
        resume_list = serializers.serialize('json', resume_list)
        return JsonResponse({'status': 'successful', 'hunter_position_list': hunter_position_list,'position_list': position_list,'interview_list': interview_list,'company_list':company_list,'company_resume_list':company_resume_list,'resume_list':resume_list})
    else:
        return render(request, 'backend/hunter/myDeliver.html')

#求职者查看我的收藏
def myCollect(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id=request.session.get('user_id')
        hunter=Hunter.objects.filter(user_id=user_id).first()
        hunterPositions=HunterPosition.objects.filter(hunter_id=hunter.id)
        position_list=[]
        company_list=[]
        print(hunterPositions)
        for hunterPosition in hunterPositions:
            if hunterPosition.is_collect=='1':
                position=Position.objects.filter(id=hunterPosition.position_id).first()
                position_list.append(position)
                company_list.append(Company.objects.filter(company_name=position.company_name_id).first())
        position_list = serializers.serialize('json', position_list)
        company_list = serializers.serialize('json', company_list)
        return JsonResponse({'status': 'successful', 'position_list': position_list, 'company_list': company_list})
    else:
        return render(request,'backend/hunter/myCollect.html')

#求职者删除收藏的职位信息
def myCollectDelete(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position_id_list = request.POST.get('id_list')
        position_id_list = position_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        user_id = request.session.get('user_id')
        hunter = Hunter.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        for i in position_id_list:
            hunterPosition = HunterPosition.objects.filter(hunter_id=hunter.id, position_id=i).first()
            if hunterPosition.status!='无':
                hunterPosition.is_collect='0'
            else:
                hunterPosition.delete()
        return JsonResponse(ret)


#公司首页
def company_index(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    return render(request,'backend/company/company_index.html')



#公司注册表单
def companyForm(request):
    if request.method == 'POST':
        company_form = forms.CompanyForm(request.POST)
        user_id = request.session.get('user_id')
        print(user_id)
        if company_form.is_valid():
            company_form = company_form.save(commit=False)
            company_form.user_id = user_id
            #未审核
            company_form.status = '0'
            company_form.save()
            return JsonResponse({'status': 'successful'})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = company_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            print(json.dumps(ret))
            return HttpResponse(json.dumps(ret))
    else:
        return render(request,'backend/company/companyForm.html')

#公司基本信息修改,参数user_id
def company_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        id=request.session.get('user_id')
        user=User.objects.filter(id=id).first()
        user_form = forms.UserForm(request.POST, instance=user)
        company=Company.objects.filter(user_id=id).first()
        company_form = forms.CompanyForm(request.POST,instance=company)
        if user_form.is_valid() & company_form.is_valid():
            user_form.save()#更新最后登录时间
            company_form=company_form.save(commit=False)
            company_form.status='2'#企业信息变更，等待管理员处理
            company_form.save()
            return JsonResponse({'status': 'successful'})
        elif not user_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = user_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
        else:
            ret = {'status': 'successful', 'errs': None}
            error = company_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

    else:
        return render(request,'backend/company/companyForm.html')
#显示公司基本信息和职位信息
def company_show(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if  request.method=='POST':
        user_list=[]
        company_list = []
        position_list=[]
        user = User.objects.filter(id=request.session.get('user_id')).first()
        company = Company.objects.filter(user=user).first()
        # company=user.company#反向引用，等同于上面
        user_list.append(user)
        company_list.append(company)
        user_list = serializers.serialize('json', user_list)
        company_list = serializers.serialize('json', company_list)
        #职位：正在招聘与暂停招聘
        position_list = Position.objects.filter(company_name=company.company_name,is_delete__in=['0','2']).order_by('-id')
        #编辑
        if position_list:
            position_list = serializers.serialize('json', position_list)
            return JsonResponse({'user_list':user_list,'company_list':company_list,'position_list':position_list})
        return JsonResponse({'user_list':user_list,'company_list':company_list})
    # 请求页面
    else:
        return render(request, 'backend/company/company.html')
#公司职位添加
def position_add(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        position_form = forms.PositionForm(request.POST)
        user_id = request.session.get('user_id')
        company=Company.objects.filter(user_id=user_id).first()
        if position_form.is_valid():
            position_form = position_form.save(commit=False)
            #人数转换为整形
            position_form.count=int(request.POST.get("count"))
            # position_form.company_id = company.id
            position_form.company_name= company
            position_form.save()
            position_list = []
            position = Position.objects.last()
            position_list.append(position)
            position_list = serializers.serialize('json', position_list)
            return JsonResponse({'status': 'successful', 'position_list': position_list})

        else:
            ret = {'status': 'successful', 'errs': None}
            error = position_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

#公司职位信息修改
def position_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        position=Position.objects.filter(id=id).first()
        position_form = forms.PositionForm(request.POST,instance=position)
        if position_form.is_valid():
            position_form.save()
            position_list = []
            position = Position.objects.last()
            position_list.append(position)
            position_list = serializers.serialize('json', position_list)
            return JsonResponse({'status': 'successful', 'position_list': position_list})
        else:
            ret = {'status': 'successful', 'errs': None}
            error = position_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
#公司进行职位逻辑删除；企业无法查看、求职者收藏与投递反馈界面可查看
def position_del(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position = Position.objects.filter(id=id).first()
        position.is_delete='1'
        if position.save():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })


#管理员查看职位信息
def positions(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        response = {}
        # 逆序
        position_list = Position.objects.all().order_by("-id")
        paginator = Paginator(position_list, pageSize)
        response['total'] = paginator.count
        try:
            positions = paginator.page(page)
        except PageNotAnInteger:
            positions = paginator.page(1)
        except EmptyPage:
            positions = paginator.page(paginator.num_pages)
        response['position_list'] = serializers.serialize("json", positions)
        return JsonResponse(response)
    else:
        return render(request,'backend/admin/positions.html')

#管理员直接删除职位（单个）
def position_del_admin(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        position = Position.objects.filter(id=id).first()
        if position.delete():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })

#管理员删除职位信息（多个）
def positions_del(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        print(request.POST)
        position_id_list = request.POST.get('id_list')
        position_id_list = position_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        ret = {'status': 'successful', 'errs': None}
        for i in position_id_list:
            position =Position.objects.filter(id=i).first()
            position.delete()
        return JsonResponse(ret)


#管理员修改用户（求职者）信息
def hunter_edit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        user=User.objects.filter(id=id).first()
        user_form = forms.UserForm(request.POST,instance=user)
        hunter=Hunter.objects.filter(user_id=user.id).first()
        hunter_form=forms.HunterForm(request.POST,instance=hunter)
        resume=Resume.objects.filter(hunter_id=hunter.id).first()
        resume_form=forms.ResumeForm(request.POST,instance=resume)
        if user_form.is_valid() & hunter_form.is_valid() & resume_form.is_valid():
            user_form.save()
            hunter_form.save()
            resume_form.save()
            user_list = []
            hunter_list = []
            resume_list = []
            user = User.objects.last()
            hunter = Hunter.objects.last()
            resume = Resume.objects.last()
            user_list.append(user)
            hunter_list.append(hunter)
            resume_list.append(resume)
            user_list = serializers.serialize('json', user_list)
            hunter_list = serializers.serialize('json', hunter_list)
            resume_list = serializers.serialize('json', resume_list)
            return JsonResponse({'status': 'successful', 'user_list': user_list,'hunter_list': hunter_list,'resume_list': resume_list})
        elif not user_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = user_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
        elif not hunter_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = hunter_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
        else:
            ret = {'status': 'successful', 'errs': None}
            error = resume_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

#管理员修改用户（企业）信息
def companyEditByAdmin(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        user=User.objects.filter(id=id).first()
        user_form = forms.UserForm(request.POST,instance=user)
        company = Company.objects.filter(user_id=user.id).first()
        company_form = forms.CompanyForm(request.POST, instance=company)
        if user_form.is_valid() & company_form.is_valid() :
            user_form.save()
            company_form.save()
            user_list = []
            company_list = []
            resume_list = []
            user = User.objects.last()
            company = Company.objects.last()
            user_list.append(user)
            company_list.append(company)
            user_list = serializers.serialize('json', user_list)
            company_list = serializers.serialize('json', company_list)
            return JsonResponse({'status': 'successful', 'user_list': user_list, 'company_list': company_list,})
        elif not user_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = user_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
        elif not company_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = company_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

#管理员查看用户信息
def users(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        user_type= request.POST.get('user_type')
        response = {}
        hunter_list=[]
        resume_list=[]
        company_list=[]
        user_list = User.objects.filter(user_type=user_type).order_by("id")
        #求职者
        if user_type=='1':
            for user in user_list:
                hunter=Hunter.objects.filter(user_id=user.id).first()
                hunter_list.append(hunter)
                resume=Resume.objects.filter(hunter_id=hunter.id).first()
                resume_list.append(resume)
            paginator_hunter = Paginator(hunter_list, pageSize)
            paginator_user = Paginator(user_list, pageSize)
            paginator_resume = Paginator(resume_list, pageSize)
            response['total'] = paginator_user.count
            try:
                users = paginator_user.page(page)
                hunters = paginator_hunter.page(page)
                resumes = paginator_resume.page(page)
            except PageNotAnInteger:
                users = paginator_user.page(1)
                hunters = paginator_hunter.page(1)
                resumes = paginator_resume.page(1)
            except EmptyPage:
                users = paginator_user.page(paginator_user.num_pages)
                hunters = paginator_hunter.page(paginator_hunter.num_pages)
                resumes = paginator_resume.page(paginator_resume.num_pages)
            response['user_list'] = serializers.serialize("json", users)
            response['hunter_list'] = serializers.serialize("json", hunters)
            response['resume_list'] = serializers.serialize("json", resumes)
            return JsonResponse(response)
        #企业
        elif user_type=='2':
            for user in user_list:
                company=Company.objects.filter(user_id=user.id).first()
                company_list.append(company)
            paginator_user = Paginator(user_list, pageSize)
            paginator_company = Paginator(company_list, pageSize)
            response['total'] = paginator_user.count
            try:
                users = paginator_user.page(page)
                companys = paginator_company.page(page)
            except PageNotAnInteger:
                users = paginator_user.page(1)
                companys = paginator_company.page(1)
            except EmptyPage:
                users = paginator_user.page(paginator_user.num_pages)
                companys = paginator_company.page(paginator_company.num_pages)
            response['user_list'] = serializers.serialize("json", users)
            response['company_list'] = serializers.serialize("json", companys)
            return JsonResponse(response)
        #管理员
        elif user_type=='3':
            paginator_user = Paginator(user_list, pageSize)
            response['total'] = paginator_user.count
            try:
                users = paginator_user.page(page)
            except PageNotAnInteger:
                users = paginator_user.page(1)
            except EmptyPage:
                users = paginator_user.page(paginator_user.num_pages)
            response['user_list'] = serializers.serialize("json", users)
            return JsonResponse(response)
    else:
        return render(request,'backend/admin/users.html')

#管理员删除用户信息（多个）
def users_del(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        try:
            with transaction.atomic():#事务回滚
                user_id_list = request.POST.get('id_list')
                user_id_list = user_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
                ret = {'status': 'successful', 'errs': None}
                print('删除')
                for i in user_id_list:
                    # user =User.objects.filter(id=i).first()
                    user_del(request, i)#级联删除
                return JsonResponse(ret)
        except Exception as e:
            ret['status']='warning'
            ret['errs']=str(e)
            return JsonResponse(ret)
            # return HttpResponse("出现错误<%s>" % str(e))
#公司、管理员职位删除（单个）
def user_del(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user = User.objects.filter(id=id).first()
        if user.delete():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status':"fail"
            })

#超级管理员创建管理员
def adminAdd(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        try:
            ret = {'status': 'successful', 'errs': None}
            user_form=forms.UserForm(request.POST)
            if user_form.is_valid():
                user_form=user_form.save(commit=False)
                user_form.user_password=get_md5(request.POST.get('user_email'),request.POST.get('user_password'))
                user_form.save()
            else:
                error = user_form.errors
                ret['status'] = 'fail'
                ret['errs'] = error.as_json()
                return HttpResponse(json.dumps(ret))
        except Exception as e:
            ret['errs']=str(e)
            ret['status']='warning'
        return JsonResponse(ret)

#管理员修改用户信息
def adminEdit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        user=User.objects.filter(id=id).first()
        user_form = forms.UserForm(request.POST,instance=user)
        if user_form.is_valid() :
            user_form = user_form.save(commit=False)
            user_form.user_password = get_md5(request.POST.get('user_email'), request.POST.get('user_password'))
            user_form.save()
            user_list = []
            user = User.objects.last()
            user_list.append(user)
            user_list = serializers.serialize('json', user_list)
            return JsonResponse({'status': 'successful', 'user_list': user_list})
        elif not user_form.is_valid():
            ret = {'status': 'successful', 'errs': None}
            error = user_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))



#企业查看收藏的简历
def getResumeCollect(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id=request.session.get('user_id')
        company=Company.objects.filter(user_id=user_id).first()
        companyResumes=CompanyResume.objects.filter(company_id=company.id)
        resume_list=[]
        user_list=[]
        hunter_list = []
        for companyResume in companyResumes:
            if companyResume.is_collect=='1':
                resume=Resume.objects.filter(id=companyResume.resume_id).first()
                if resume:
                    resume_list.append(resume)
                #求职者简历已被删除，企业无法查看
                else:
                    resume = Resume()
                    resume.resume_name = '简历已被删除'
                    resume_list.append(resume)
                hunter=Hunter.objects.filter(id=resume.hunter_id).first()
                hunter_list.append(hunter)
                user = User.objects.filter(id=hunter.user_id).first()
                user_list.append(user)
        company_resume_list = serializers.serialize('json', companyResumes)
        resume_list = serializers.serialize('json', resume_list)
        user_list = serializers.serialize('json', user_list)
        hunter_list = serializers.serialize('json', hunter_list)
        return JsonResponse({'status': 'successful', 'company_resume_list':company_resume_list,'resume_list': resume_list,'user_list': user_list,'hunter_list': hunter_list})
    else:
        return render(request,'backend/company/companyCollect.html')

#企业查看所有简历
def getAllResume(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        user_list = []
        hunter_list = []
        resume_list=Resume.objects.all().order_by("-refresh_time")
        paginator = Paginator(resume_list, pageSize)
        try:
            resumes = paginator.page(page)
        except PageNotAnInteger:
            resumes = paginator.page(1)
        except EmptyPage:
            resumes = paginator.page(paginator.num_pages)
        for resume in resumes:
            hunter=Hunter.objects.filter(id=resume.hunter_id).first()
            user=User.objects.filter(id=hunter.user_id).first()
            user_list.append(user)
            hunter_list.append(hunter)
        user_list = serializers.serialize('json', user_list)
        hunter_list = serializers.serialize('json', hunter_list)
        resume_list = serializers.serialize('json', resume_list)
        return JsonResponse({'status': 'successful','total':paginator.count, 'resume_list': resume_list,'user_list': user_list,'hunter_list': hunter_list})
    else:
        return render(request, 'backend/company/resume_search.html')
#企业收藏简历
def resumeCollect(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        resume_id_list = request.POST.get('id_list')
        resume_id_list = resume_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        user_id=request.session.get('user_id')
        company=Company.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        try:
            for i in resume_id_list:
                 companyResume=CompanyResume.objects.filter(company_id=company.id,resume_id=i).first()
                 if companyResume:
                     if companyResume.is_collect=='0':
                         companyResume.is_collect='1'
                         companyResume.collect_time=timezone.now()
                         companyResume.save()
                     else:
                        pass
                     # message = '您已收藏！'
                     # ret['status'] = 'warning'
                     # ret['errs'] = message
                     # return JsonResponse(ret)
                 else:
                    resume=Resume.objects.get(id=i)
                    companyResume=CompanyResume(company=company,resume=resume,is_collect='1',collect_time=timezone.now())
                    companyResume.save()
            return JsonResponse({'status': 'successful'})
        except Exception as e:
            ret['status']='warning'
            ret['errs']=e
        return JsonResponse(ret)
#企业删除收藏的简历
def myCollectDelete(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        resume_id_list = request.POST.get('id_list')
        resume_id_list = resume_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        user_id = request.session.get('user_id')
        company = Company.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        for i in resume_id_list:
            companyResume = CompanyResume.objects.filter(company_id=company.id, resume_id=i).first()
            if companyResume.status!='无':
                companyResume.is_collect='0'
            else:
                companyResume.delete()
        return JsonResponse(ret)

#企业查看所有投递却未处理的简历
def getPositionDeliver(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id = request.session.get('user_id')
        company = Company.objects.get(user_id=user_id)
        status = request.POST.get('activeName')
        if status=='unHandel':
            status='deliver'
        positions=Position.objects.filter(company_name=company.company_name,is_delete='0')
        ret = {'status': 'successful', 'errs': None}
        hunter_position_list=[]
        position_list=[]
        hunter_list=[]
        resume_list=[]
        interview_list=[]
        company_resume_list=[]
        for i in positions:
            hunterPositions = HunterPosition.objects.filter(position_id=i.id)
            if hunterPositions:
                for j in hunterPositions:
                    if j.status == status:
                        print(j.resume)
                        hunter_position_list.append(j)
                        position_list.append(Position.objects.filter(id=j.position_id,is_delete='0').first())
                        hunter_list.append(Hunter.objects.filter(id=j.hunter_id).first())
                        resume=Resume.objects.filter(id=j.resume).first()
                        if resume:
                            resume_list.append(resume)
                        else:
                            resume=Resume()
                            resume.resume_name='简历已被删除'
                            resume_list.append(resume)
                        if status=='interview':
                            interview_list.append(Interview.objects.filter(id=j.interview_id).first())

        if status=='interview':
            companyResumes = CompanyResume.objects.filter(company_id=company.id)
            if companyResumes:
                for j in companyResumes:
                    if j.status == status:
                        company_resume_list.append(j)
                        # position_list.append(Position.objects.filter(id=j.position_id, is_delete='0').first())
                        hunter_id=Resume.objects.filter(id=j.resume_id).first().hunter_id
                        hunter_list.append(Hunter.objects.filter(id=hunter_id).first())
                        resume = Resume.objects.filter(id=j.resume_id).first()
                        if resume:
                            resume_list.append(resume)
                        else:
                            resume = Resume()
                            resume.resume_name = '简历已被删除'
                            resume_list.append(resume)
                        interview_list.append(Interview.objects.filter(id=j.interview_id).first())
        hunter_position_list = serializers.serialize('json', hunter_position_list)
        company_resume_list = serializers.serialize('json', company_resume_list)
        position_list = serializers.serialize('json', position_list)
        hunter_list = serializers.serialize('json', hunter_list)
        print(resume_list)
        resume_list = serializers.serialize('json', resume_list)
        interview_list = serializers.serialize('json', interview_list)
        print(interview_list)
        return JsonResponse({'status': 'successful','resume_list':resume_list, 'hunter_position_list':hunter_position_list,'company_resume_list':company_resume_list,'position_list': position_list,'hunter_list':hunter_list,'interview_list':interview_list})
# 企业查看简历投递数量：上标
def getPositionDeliverCount(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id = request.session.get('user_id')
        company = Company.objects.get(user_id=user_id)
        positions=Position.objects.filter(company_name=company.company_name,is_delete='0')
        ret = {'status': 'successful', 'errs': None}
        deliverCount=0
        checkedCount = 0
        interviewCount = 0
        improperCount = 0
        count=[]
        for i in positions:
            hunterPositions = HunterPosition.objects.filter(position_id=i.id)
            if hunterPositions:
                for j in hunterPositions:
                    print(j.status)
                    if j.status == 'improper':
                        improperCount=improperCount+1
                    elif j.status == 'deliver':
                        deliverCount = deliverCount + 1
                    elif j.status == 'checked':
                        checkedCount = checkedCount + 1
                    elif j.status == 'interview':
                        interviewCount = interviewCount + 1
        count.append(deliverCount)
        count.append(checkedCount)
        count.append(interviewCount)
        count.append(improperCount)
        return JsonResponse({'status': 'successful','count':count})

#企业处理简历投递，根据hangdelmethod处理为有意向、不合适、面试邀请
def resumeManage(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        position_id_list = request.POST.get('id_list')
        handelMethod = request.POST.get('handelMethod')
        print(handelMethod)
        position_id_list = position_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        ret = {'status': 'successful', 'errs': None}
        for i in position_id_list:
            hunterPosition = HunterPosition.objects.filter(id=i).first()
            if (hunterPosition.status == "deliver" )| (hunterPosition.status == "checked"):
                hunterPosition.status = handelMethod
                hunterPosition.save()
                # return JsonResponse(ret)
            else:
                pass
                #     message = '您已申请该职位！'
                #     ret['status'] = 'warning'
                #     ret['errs'] = message
                #     return JsonResponse(ret)
        return JsonResponse(ret)
    else:
        return render(request,'backend/company/resumeManage.html')
#企业对投递的简历发送面试邀请
def interviewAdd(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        interview_form=forms.InterviewForm(request.POST)
        ret = {'status': 'successful', 'errs': None}
        if interview_form.is_valid():
            interview_form.save(commit=False)
            id=request.POST.get('id')
            hunterPosition=HunterPosition.objects.filter(id=id).first()
            hunter_id=hunterPosition.hunter_id
            user_id=Hunter.objects.filter(id=hunter_id).first().user_id
            email=User.objects.filter(id=user_id).first().user_email
            ret = '面试时间：'+interview_form.cleaned_data['time'].strftime("%Y-%m-%d %H:%M:%S")+'\n'+interview_form.cleaned_data['content']
            # 给邮箱发送验证码
            # status=1
            status = send_mail(interview_form.cleaned_data['title'], ret, EMAIL_FROM, [email], fail_silently=False)
            if not status == 1:
                print('邮箱发送失败')
                ret['status']='warning'
                ret['errs']="邮件发送失败"
                return JsonResponse(ret,safe=False)
            interview_form=interview_form.save()
            hunterPosition.status='interview'
            hunterPosition.interview_id=interview_form.id
            hunterPosition.save()
            return JsonResponse({'status':'successful'})
        else:
            error = interview_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
# 企业在搜索界面主动进行面试邀请，参数：简历id、面试邀请表单，修改企业简历表、面试邀请表。
def resumeInterview(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id=request.session.get('user_id')
        company=Company.objects.get(user_id=user_id)
        ret = {'status': 'successful', 'errs': None}
        id = request.POST.get('id')  # 简历id
        print(id)
        interview_form = forms.InterviewForm(request.POST)
        if interview_form.is_valid():
            interview_form.save(commit=False)
            companyResume = CompanyResume.objects.filter(company_id=company.id, resume_id=id).first()
            # 已收藏
            if companyResume:
                if companyResume.status == "无":
                    companyResume.status = 'interview'
            # 未收藏
            else:
                resume=Resume.objects.filter(id=id).first()
                companyResume=CompanyResume(company=company,resume=resume,status='interview')
            hunter_id = Resume.objects.filter(id=id).first().hunter_id
            hunter=Hunter.objects.filter(id=hunter_id).first()
            user=User.objects.filter(id=hunter.user_id).first()
            email = user.user_email
            ret = '面试时间：' + interview_form.cleaned_data['time'].strftime("%Y-%m-%d %H:%M:%S") + '\n' + \
                  interview_form.cleaned_data['content']
            # 给邮箱发送验证码
            status = send_mail(interview_form.cleaned_data['title'], ret, EMAIL_FROM, [email], fail_silently=False)
            if not status == 1:
                print('邮箱发送失败')
                ret['status'] = 'warning'
                ret['errs'] = "邮件发送失败"
                return JsonResponse(ret, safe=False)
            interview_form = interview_form.save()
            companyResume.time=timezone.now()
            companyResume.interview_id = interview_form.id
            companyResume.save()
            return JsonResponse({'status': 'successful'})
        else:
            error = interview_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()

#企业主动发送面试邀请求职者（职位已被收藏）
def companyInterviewAdd(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        interview_form=forms.InterviewForm(request.POST)
        ret = {'status': 'successful', 'errs': None}
        if interview_form.is_valid():
            interview_form.save(commit=False)
            id=request.POST.get('id')#主动面试邀请表id
            companyResume=CompanyResume.objects.filter(id=id).first()
            resume_id=companyResume.resume_id
            resume=Resume.objects.filter(id=resume_id).first()
            user_id=Hunter.objects.filter(id=resume.hunter_id).first().user_id
            email=User.objects.filter(id=user_id).first().user_email
            ret = '面试时间：'+interview_form.cleaned_data['time'].strftime("%Y-%m-%d %H:%M:%S")+'\n'+interview_form.cleaned_data['content']
            # 给邮箱发送验证码
            status = send_mail(interview_form.cleaned_data['title'], ret, EMAIL_FROM, [email], fail_silently=False)
            if not status == 1:
                print('邮箱发送失败')
                print('l')
                ret['status']='warning'
                ret['errs']="邮件发送失败"
                return JsonResponse(ret,safe=False)
            interview_form=interview_form.save()
            companyResume.status='interview'
            companyResume.interview_id=interview_form.id
            companyResume.time=timezone.now()
            companyResume.save()
            return JsonResponse({'status':'successful'})
        else:
            error = interview_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))

#企业查看面试日程（所有）
def getInterview(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user_id = request.session.get('user_id')
        company = Company.objects.get(user_id=user_id)
        positions=Position.objects.filter(company_name=company.company_name,is_delete='0')
        interview_list=[]
        for i in positions:
            hunterPositions = HunterPosition.objects.filter(position_id=i.id)
            if hunterPositions:
                for j in hunterPositions:
                    if j.status == 'interview':
                        interview=Interview.objects.filter(id=j.interview_id).first()
                        interview_list.append(interview)
        for i in positions:
            companyResumes = CompanyResume.objects.filter(company_id=company.id)
            if companyResumes:
                for j in companyResumes:
                    if j.status == 'interview':
                        interview=Interview.objects.filter(id=j.interview_id).first()
                        interview_list.append(interview)
        interview_list = serializers.serialize('json', interview_list)
        return JsonResponse( {'status': 'successful', 'interview_list': interview_list})


#管理员首页
def admin_index(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    return render(request, 'backend/admin/admin_index.html')

#数据可视化
def echarts(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    return render(request,'backend/admin/echarts.html')

#查看各类别用户总量
def getUserNum(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        hunter_list=User.objects.filter(user_type='1')
        company_list = User.objects.filter(user_type='2')
        admin_list = User.objects.filter(user_type='3')
        num_list=[]
        num_list.append(hunter_list.count())
        num_list.append(company_list.count())
        num_list.append(admin_list.count())
        ret['status'] = 'successful'
        ret['num_list'] = num_list
        return HttpResponse(json.dumps(ret))
#查看性别分布
def getUserSex(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        males=Hunter.objects.filter(sex='0')
        females = Hunter.objects.filter(sex='1')
        num_list=[]
        num_list.append(males.count())
        num_list.append(females.count())
        ret['status'] = 'successful'
        ret['num_list'] = num_list
        return HttpResponse(json.dumps(ret))
#统计连续五个月的用户注册量
def userStatistics(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        ret = {'status': 'successful', 'errs': None}
        month = timezone.now().month
        print(month)
        month_copy=month
        year = timezone.now().year
        num_list = []
        month_list=[]
        hunter_list = []
        company_list = []
        # 包括去年
        if month-12<0:
            index=0-month+12
            for i in range(index) :
                month = 12 - index+1+i
                users = User.objects.filter(creat_time__year=year-1, creat_time__month=month)
                num_list.append(users.count())
                month_list.append(month)
                hunter = 0
                company = 0
                for user in users:
                    if user.user_type == '1':
                        hunter = hunter + 1
                    elif user.user_type == '2':
                        company = company + 1
                hunter_list.append(hunter)
                company_list.append(company)

            for i in range(month_copy) :
                month = 1+i
                users = User.objects.filter(creat_time__year=year, creat_time__month=month)
                num_list.append(users.count())
                month_list.append(month)
                hunter = 0
                company = 0
                for user in users:
                    if user.user_type == '1':
                        hunter = hunter + 1
                    elif user.user_type == '2':
                        company = company + 1
                hunter_list.append(hunter)
                company_list.append(company)
        #从今年5月
        else:
            month = month_copy + 1 - 12
            for i in range(12):
                users = User.objects.filter(creat_time__year=year, creat_time__month=month+i)
                hunter=0
                company=0
                for user in users:
                    if user.user_type=='1':
                        hunter=hunter+1
                    elif user.user_type=='2':
                        company=company+1
                hunter_list.append(hunter)
                company_list.append(company)
                num_list .append(users.count())
                month_list.append(month+i)
        ret['status'] = 'successful'
        ret['num_list'] = num_list
        ret['month_list'] = month_list
        ret['hunter_list'] = hunter_list
        ret['company_list'] = company_list
        print(month_list)
        return HttpResponse(json.dumps(ret))
#职位学历要求比例
def educationRequirement(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        positions=Position.objects.all()
        num_list=[0,0,0,0,0]
        for position in positions:
            if position.education_requirement=='专科':
                num_list[0]=num_list[0]+1
            elif position.education_requirement=='本科':
                num_list[1]=num_list[1]+1
            elif position.education_requirement=='硕士':
                num_list[2]=num_list[2]+1
            elif position.education_requirement=='博士':
                num_list[3]=num_list[3]+1
            elif position.education_requirement=='其他':
                num_list[4]=num_list[4]+1
        ret['num_list'] = num_list
        return HttpResponse(json.dumps(ret))

#职位地区分布
def cityDistribute(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        ret = {'status': 'successful', 'errs': None}
        positions = Position.objects.all()
        city_list=[]
        num_list=[]
        flag = False
        for position in positions:
            workplace=position.workplace
            for i in range(len(city_list)):
                if workplace==city_list[i]:
                    num_list[i]=num_list[i]+1
                    flag=True
                    break
            if flag==False:
                city_list.append(workplace)
                num_list.append(1)
        ret['city_list'] = city_list
        ret['num_list'] = num_list
        return HttpResponse(json.dumps(ret))
#待处理的公司审核
def getStatusHandel(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        company_list=Company.objects.filter(status='0')
        user_list=[]
        print(company_list)
        for company in company_list:
            user=User.objects.filter(id=company.user_id).first()
            user_list.append(user)
        user_list = serializers.serialize('json', user_list)
        company_list = serializers.serialize('json', company_list)
        return JsonResponse({'status':'successful','user_list': user_list,'company_list':company_list})
#企业审核通过
def statusToPass(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        company_id_list = request.POST.get('id_list')
        company_id_list = company_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        for id in company_id_list:
            company=Company.objects.filter(id=id).first()
            user=User.objects.filter(id=company.user_id).first()
            company.status="1"
            ret="您好，贵公司信息已审核通过，欢迎您使用本系统！"
            status=send_mail('审核状态通知', ret, EMAIL_FROM, [user.user_email], fail_silently=False)
            if not status == 1:
                return JsonResponse({
                    'status': 'warning',
                    'errs': "邮件发送失败",
                })
            company.save()
        return JsonResponse(ret)


# 企业审核不通过
def statusToFail(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        company_id_list = request.POST.get('id_list')
        company_id_list = company_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        for id in company_id_list:
            company = Company.objects.filter(id=id).first()
            user = User.objects.filter(id=company.user_id).first()
            # company.status = "3"#管理员查看到未通过信息
            ret = "您好，很抱歉，贵公司信息经审核未通过。请使用真实信息注册本系统，以便后续工作！"
            status=send_mail('审核状态通知', ret, EMAIL_FROM, [user.user_email], fail_silently=False)
            if not status == 1:
                return JsonResponse({
                    'status': 'warning',
                    'errs': "邮件发送失败",
                })
            company.delete()#将未通过的信息进行删除
        return JsonResponse(ret)

# 企业查看最近一周的面试日程9:00-17:00
def interviewByWeek(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        #该公司所有面试
        q=0
        interview_list=[]
        #同一时间段符合要求的面试详情
        interview_time_list=[]
        #连续五天
        interview_list_list=[]
        # 获取当前时间
        now = datetime.datetime.now()
        #获取今天零点
        user_id = request.session.get('user_id')
        company = Company.objects.get(user_id=user_id)
        positions = Position.objects.filter(company_name=company.company_name, is_delete='0')
        if positions:
            for i in positions:
                hunterPositions = HunterPosition.objects.filter(position_id=i.id)
                if hunterPositions:
                    for j in hunterPositions:
                        if j.status == 'interview':
                            q=q+1
                            if q>1:
                                interviewNext= Interview.objects.filter(id=j.interview_id)
                                interview1=interview1|interviewNext
                            else:
                                interview1 = Interview.objects.filter(id=j.interview_id)
        i=0
        companyResumes = CompanyResume.objects.filter(company_id=company.id)
        if companyResumes:
            for j in companyResumes:
                if j.status == 'interview':
                    i = i + 1
                    if i > 1:
                        interviewNext = Interview.objects.filter(id=j.interview_id)
                        interview2 = interview2 | interviewNext
                    else:
                        interview2 = Interview.objects.filter(id=j.interview_id)
        interviewAll=interview2|interview1
        start = datetime.timedelta(hours=9)
        other= datetime.timedelta(hours=10)
        for i in range(8):
            #清空，存储下一时间段
            interview_time_list=[]
            zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                                 microseconds=now.microsecond)
            for i in range(5):
                start_date = zeroToday + start
                other_date = zeroToday + other
                print(start_date)
                interview = interviewAll.filter(time__lt=other_date,time__gte=start_date).first()
                if interview:
                    interview_time_list.append(interview.title)
                else:
                    interview_time_list.append(' ')
                zeroToday = zeroToday + datetime.timedelta(days=1)
            start= other
            other= other+ datetime.timedelta(hours=1)
            print(interview_time_list)
            interview_list_list.append(interview_time_list)
        week_list=[]
        week=now.weekday()
        if week>1:
            for i in range(5):
                week_list.append(week)
                week = week + 1
                if week>6:
                    week=0
        else:
            for i in range(5):
                week_list.append(week)
                week = week + 1
        for i in range(len(week_list)):
            if week_list[i]==0:
                week_list[i]='星期一'
            if week_list[i] == 1:
                week_list[i] = '星期二'
            if week_list[i] ==2:
                week_list[i] = '星期三'
            if week_list[i]==3:
                week_list[i]='星期四'
            if week_list[i]==4:
                week_list[i]='星期五'
            if week_list[i]==5:
                week_list[i]='星期六'
                print(week_list[i])
            if week_list[i]==6:
                week_list[i]='星期日'
        # interview_list = serializers.serialize('json', interview_list)
        print(week_list)
        return JsonResponse({'status': 'successful','week_list':week_list, 'interview_list_list': interview_list_list})
    else:
        return render(request,'backend/test.html')
#管理员发布新闻
def newsAdd(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        ret = {'status': 'successful', 'errs': None}
        news_form=forms.NewsForm(request.POST)
        if news_form.is_valid():
            news_form=news_form.save(commit=False)
            news_form.user_id=request.session.get('user_id')
            news_form.save()
            return HttpResponse(json.dumps(ret))
        else:
            error = news_form.errors
            ret['status'] = "fail"
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))
    else:
        return render(request, 'backend/admin/news.html')
#管理员删除新闻
def newsDel(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        news = News.objects.filter(id=id).first()
        if news.delete():
            return JsonResponse({
                'status': "successful"
            })
        else:
            return JsonResponse({
                'status': "fail"
            })
#管理员删除新闻信息（多条）
def newssDel(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        print(request.POST)
        news_id_list = request.POST.get('id_list')
        news_id_list = news_id_list.replace('[', '').replace(']', '').strip('\'').split(',')
        ret = {'status': 'successful', 'errs': None}
        for i in news_id_list:
            news =News.objects.filter(id=i).first()
            news.delete()
        return JsonResponse(ret)
#求职者、企业查看新闻（最近五条）
def newsShow(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == "POST":
        news_list = News.objects.all().order_by('-id')[:5]
        news_list = serializers.serialize('json', news_list)
        return JsonResponse({'status': 'successful', 'news_list': news_list})

#查看新闻细节
def newsDetail1(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    # if request.method == "GET":
        # id=request.GET.get('id')
    news = News.objects.filter(id=id).first()
    nextNews = News.objects.filter(id__lt=id).all().order_by("-id").first()
    if request.session.get('user_type')=='1':
        return render(request, 'backend/hunter/newsDetail.html', locals())
    elif request.session.get('user_type')=='2':
        return render(request, 'backend/company/newsDetail.html', locals())

def newsDetail(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == "GET":
        id=request.GET.get('id')
        news = News.objects.filter(id=id).first()
        nextNews = News.objects.filter(id__lt=id).all().order_by("-id").first()
        if request.session.get('user_type') == '1':
            return render(request, 'backend/hunter/newsDetail.html', locals())
        elif request.session.get('user_type') == '2':
            return render(request, 'backend/company/newsDetail.html', locals())

#管理员查看所有新闻信息
def news(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        response = {}
        user_list=[]
        news_list = News.objects.all().order_by("id")
        paginator = Paginator(news_list, pageSize)
        response['total'] = paginator.count
        try:
            news = paginator.page(page)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)
        for new in news:
            user=User.objects.filter(id=new.user_id).first()
            user_list.append(user)
        response['news_list'] = serializers.serialize("json", news)
        response['user_list'] = serializers.serialize("json", user_list)
        return JsonResponse(response)

    else:
        return render(request,'backend/admin/news.html')
def newsEdit(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        ret = {'status': 'successful', 'errs': None}
        news=News.objects.filter(id=id).first()
        news_form = forms.NewsForm(request.POST,instance=news)
        if news_form.is_valid():
            news_form.save()
            return JsonResponse(ret)
        else:
            error = news_form.errors
            ret['status'] = 'fail'
            ret['errs'] = error.as_json()
            return HttpResponse(json.dumps(ret))







from .tasks import sendmail  # 引用tasks.py文件的中sendmail方法
import json

# def course(request):
#     if not request.session.get('is_login', None):
#         return redirect('/api/login/')
#     # 耗时任务，发送邮件（用delay执行方法）
#     status=sendmail.delay('test','we','1115152483@qq.com','1115152483@qq.com')
#     print(status)
#     # 其他行为
#     # print((CompanyResume.objects.filter(is_collect='1').first().collect_time-datetime.datetime.now().date()).days)
#     # print(type((CompanyResume.objects.filter(is_collect='1').first().collect_time - datetime.datetime.now().date()).days))
#     data = 'ok'
#     return HttpResponse(json.dumps(data), content_type='application/json')
#面试详情
def interviewShow(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    interview_id = request.GET.get('id')
    interview=Interview.objects.filter(id=interview_id).first()
    if request.session.get('user_type')=='2':
        return render(request, 'backend/company/interviewDetail.html',locals())
    if request.session.get('user_type')=='1':
        return render(request, 'backend/hunter/interviewDetail.html',locals())
#管理员按时间检索职位信息
def positionOrderByTime(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        print(request.POST)
        response={}
        print(request.POST.get('timeRange'))
        time=request.POST.get('timeRange').replace('[', '').replace('"','').replace(']', '').split(',')
        data_form=time[0]
        data_to=time[1]
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        position_list = Position.objects.filter(release_time__range=(data_form,data_to)).order_by("-id")
        paginator = Paginator(position_list, pageSize)
        response['total'] = paginator.count
        try:
            positions = paginator.page(page)
        except PageNotAnInteger:
            positions = paginator.page(1)
        except EmptyPage:
            positions = paginator.page(paginator.num_pages)
        # if 'year_form' and 'month_from' and 'day_form' and 'year_to' and 'month_to' and 'day_to' in request.POST:
        #     Y=request.POST['year_form']
        #     M = request.POST['month_from']
        #     D = request.POST['day_form']
        #     data_form=datetime.datetime(int(Y),int(M),int(D),0,0)
        #     y = request.POST['year_to']
        #     m = request.POST['month_to']
        #     d = request.POST['day_to']
        #     data_to = datetime.datetime(int(y), int(m), int(d), 0, 0)
        #     positions=Position.objects.filter(release_time__range=(data_form,data_to))
        response['position_list'] = serializers.serialize("json", positions)
        return JsonResponse(response)
#薪资与学历关系
def educationAndSalary(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        response={}
        positions=Position.objects.all()
        collegeSalary=0
        undergraduateSalary=0
        masterSalary=0
        doctorSalary=0
        collegeCount=0
        undergraduateCount=0
        masterCount=0
        doctorCount=0
        for position in positions:
            if position.education_requirement=='专科':
                collegeSalary=collegeSalary+int(position.pay.split('-')[1])
                collegeCount=collegeCount+1
            elif position.education_requirement=='本科':
                undergraduateSalary=undergraduateSalary+int(position.pay.split('-')[1])
                undergraduateCount = undergraduateCount + 1
            elif position.education_requirement=='硕士':
                masterSalary=masterSalary+int(position.pay.split('-')[1])
                masterCount = masterCount + 1
            elif position.education_requirement=='博士':
                doctorSalary=doctorSalary+int(position.pay.split('-')[1])
                doctorCount = doctorCount + 1
        collegeLevel=0
        undergraduateLevel = 0
        masterLevel = 0
        doctorLevel = 0
        if not collegeCount==0:
            collegeLevel=collegeSalary/collegeCount
            print(collegeCount)
            print(collegeSalary)
        if not undergraduateCount == 0:
            undergraduateLevel = undergraduateSalary / undergraduateCount
            print(undergraduateSalary)
            print(undergraduateCount)
        if not masterCount == 0:
            masterLevel = masterSalary / masterCount
            print(masterCount)
            print(masterSalary)
        if not doctorCount == 0:
            doctorLevel = doctorSalary / doctorCount
            print(doctorCount)
            print(doctorSalary)
        salary=[]
        salary.append(collegeLevel)
        salary.append(undergraduateLevel)
        salary.append(masterLevel)
        salary.append(doctorLevel)
        response['status']='successful'
        response['salary']=salary
        print(salary)
        return JsonResponse(response)

#简历pdf
from django.conf import settings
from easy_pdf.views import PDFTemplateView
import re

class HelloPDFView(PDFTemplateView):
    template_name = 'backend/pdf.html'  # html模板
    base_url = 'file://' + settings.STATIC_URL
    download_filename = 'resume.pdf'  # 下载pdf时的文件名

    def get_context_data(self, **kwargs):
        try:
            data = self.request.GET  # 可以获取请求参数
            # 注册字体，这一步操作之前，你首先要去下载msyh.ttf字体，然后放到具体某个目录下，比如我放在项目文件夹下的/front/dist/css/font/文件夹中
            pdfmetrics.registerFont(TTFont('yh', 'simkai.ttf'))
            resume_id=self.request.GET.get('id')
            print(resume_id)
            DEFAULT_FONT['helvetica'] = 'yh'
            user=User.objects.filter(id=self.request.session.get('user_id')).first()
            hunter=Hunter.objects.filter(user_id=user.id).first()
            resume=Resume.objects.filter(id=resume_id).first()
            self_assessment = resume.self_assessment
            honor=''
            print(self_assessment)
            # 写出正则表达式 任意42个字符
            if len(self_assessment)>42:
                pattern = re.compile('.{42}')
                # findall是找到所有的字符,再在字符中添加空格，当然你想添加其他东西当然也可以
                self_assessment = '\n'.join(pattern.findall(self_assessment))
            educationExperiences=EducationExperience.objects.filter(resume_id=resume.id)
            workExperiences = WorkExperience.objects.filter(resume_id=resume.id)
            projectExperiences = ProjectExperience.objects.filter(resume_id=resume.id)
            school=''
            profession=''
            honor = ''
            if educationExperiences:
                school=educationExperiences[educationExperiences.count()-1].school_name
                profession=educationExperiences[educationExperiences.count()-1].major
                for educationExperience in educationExperiences:
                    honor=honor+educationExperience.honor
                if len(honor)>42:
                    honor = '\n'.join(pattern.findall(honor))
            # photo='media\\'+str(hunter.photo)
        except Exception as e:
            print(e)
        print(self_assessment)

        return super(HelloPDFView, self).get_context_data(
            pagesize='A4',
            title='Hi there!',  # 转成pdf后文件上方的标题
            other=user,  # 也可以按需求增加自己需要的值，然后通过django的模板语言渲染到页面上
            user=user,
            hunter=hunter,
            resume=resume,
            educationExperiences=educationExperiences,
            workExperiences=workExperiences,
            projectExperiences=projectExperiences,
            school=school,
            profession=profession,
            # photo=photo,
            self_assessment=self_assessment,
            honor=honor,
            # count=count,
            # str='燕山大学三好学生优秀毕业生优秀共青团员优秀班秀毕业生优秀共青团员优秀班干部竞赛校赛校'+'\n'+'级三等奖、...竞赛国家二等奖等等。大大大大大大大版权声明：\n本文为CSDN博主「weixin_44086338」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文',
            **kwargs
        )
#求职者查看职位详情get
def positionDetail(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    id=request.GET.get('id')
    ret = {'status': 'successful', 'errs': None}
    position=Position.objects.filter(id=id).first()
    company=Company.objects.filter(company_name=position.company_name_id).first()
    return render(request,'backend/hunter/positionDetail.html',locals())
#求职者查看职位详情post
def positionDetailPost(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    ret = {'status': 'successful', 'errs': None}
    position = Position.objects.filter(id=id).first()
    company = Company.objects.filter(company_name=position.company_name_id).first()
    return render(request, 'backend/hunter/positionDetail.html', locals())
#求职者查看企业详情
def companyDetailPost(request,id):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    ret = {'status': 'successful', 'errs': None}
    company=Company.objects.filter(id=id).first()
    user=User.objects.filter(id=company.user_id).first()
    positions=Position.objects.filter(company_name=company.company_name,is_delete='0')
    return render(request,'backend/hunter/companyDetail.html',locals())
#求职者查看企业详情
def companyDetail(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    ret = {'status': 'successful', 'errs': None}
    id=request.GET.get('id')
    company=Company.objects.filter(id=id).first()
    user=User.objects.filter(id=company.user_id).first()
    positions=Position.objects.filter(company_name=company.company_name,is_delete='0')
    return render(request,'backend/hunter/companyDetail.html',locals())
#求职者查看职位详情get
def resumeDetail(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    id=request.GET.get('id')
    ret = {'status': 'successful', 'errs': None}
    resume=Resume.objects.filter(id=id).first()
    hunter=Hunter.objects.filter(id=resume.hunter_id).first()
    user = User.objects.filter(id=hunter.user_id).first()
    educationExperiences = EducationExperience.objects.filter(resume_id=resume.id)
    workExperiences = WorkExperience.objects.filter(resume_id=resume.id)
    projectExperiences = ProjectExperience.objects.filter(resume_id=resume.id)
    return render(request,'backend/company/'+resume.temp+'.html',locals())


#职位推荐
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm
def tf_similarity(s1, s2):
    def add_space(s):
        return ' '.join(list(s))
    # 将字中间加入空格
    s1, s2 = add_space(s1), add_space(s2)
    print(s1)
    # 转化为TF矩阵
    cv = CountVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))

#推荐职位
def recommendPosition(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        user=User.objects.filter(id=request.session.get('user_id')).first()
        hunter=Hunter.objects.filter(user_id=user.id).first()
        resumes=Resume.objects.filter(hunter_id=hunter.id)
        position_list=Position.objects.filter(is_delete='0')
        positions = []
        if position_list:
            if hunter.sex=='0':
                hunter.sex='男'
            elif hunter.sex == '1':
                hunter.sex = '女'
            li = []#所有职位id和相似度[[],]
            for resume in resumes:
                s1 = hunter.sex+hunter.education_background+resume.expected_work_city+resume.desired_position#resume.expected_salary
                print(s1)
                for position in position_list:
                    s4 =position.sex+position.education_requirement+position.workplace+position.position_name#position.pay
                    if float(tf_similarity(s1, s4))>0.5:
                        l = []
                        l.append(position.id)
                        l.append(float(tf_similarity(s1, s4)))
                        li.append(l)
            #存在相似度达于0.5的职位
            if li:
                #职位去重
                set=[]#唯一
                set.append(li[0])
                for item in li:
                    for items in set:
                        if item[0] != items[0]:
                            set.append(item)
                new_list1 = sorted(set, key=lambda k: k[1], reverse=True)
                # print(new_list1)

                # print(len(new_list1))
                #相似度最高的三个职位
                if len(new_list1)>=3:
                    for i in range(3):
                        position=Position.objects.filter(id=new_list1[i][0]).first()
                        positions.append(position)
                else:
                    for i in new_list1:
                        position=Position.objects.filter(id=i[0]).first()
                        positions.append(position)
        position_list = serializers.serialize('json', positions)
        return JsonResponse({'status': 'successful', 'position_list': position_list})
#推荐简历
def recommendResume(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method=='POST':
        company=Company.objects.filter(user_id=request.session.get('user_id')).first()
        positions=Position.objects.filter(company_name=company.company_name)
        resumes=Resume.objects.filter()
        resume_list=[]
        hunter_list=[]
        li = []#所有简历id\求职者id和相似度[[],]
        if positions:
            for position in positions:
                s1 = position.sex + position.education_requirement + position.workplace + position.position_name  # position.pay
                for resume in resumes:
                    hunter=Hunter.objects.filter(id=resume.hunter_id).first()
                    if hunter.sex == '0':
                        hunter.sex = '男'
                    elif hunter.sex == '1':
                        hunter.sex = '女'
                    s4 = hunter.sex + hunter.education_background + resume.expected_work_city + resume.desired_position  # resume.expected_salary
                    if float(tf_similarity(s1, s4))>0.5:
                        l = []
                        l.append(resume.id)
                        l.append(hunter.id)
                        l.append(float(tf_similarity(s1, s4)))
                        li.append(l)
            #职位去重
            set=[]#唯一
            set.append(li[0])
            for item in li:
                for items in set:
                    if item[0] != items[0]:
                        set.append(item)
            new_list1 = sorted(set, key=lambda k: k[1], reverse=True)
            # print(new_list1)
            resumes=[]
            hunters=[]
            # print(len(new_list1))
            #照相相似度最高的三个职位
            if len(new_list1)>=3:
                for i in range(3):
                    resume=Resume.objects.filter(id=new_list1[i][0]).first()
                    resumes.append(resume)
                    hunter = Hunter.objects.filter(id=new_list1[i][1]).first()
                    hunters.append(hunter)
            else:
                for i in new_list1:
                    resume=Resume.objects.filter(id=i[0]).first()
                    resumes.append(resume)
                    hunter = Hunter.objects.filter(id=i[1]).first()
                    hunters.append(hunter)
            resume_list = serializers.serialize('json', resumes)
            hunter_list = serializers.serialize('json', hunters)
        return JsonResponse({'status': 'successful', 'resume_list': resume_list,'hunter_list': hunter_list})
# def page_error(request):
#     return render(request, '500.html')


#求职者条件组合检索职位
def conditionSearch(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        condition = request.POST.get('condition')
        condition=condition.replace('[','').replace(']','').replace('"','').replace('\'','').split(',')
        education_requirement=[]
        pay = []
        workplace = []
        sex = []
        for i in condition:
            i=i.replace('{','').replace('}','')
            list=i.split(':')
            if list[0]=='education_requirement':
                education_requirement.append(list[1])
            elif list[0]=='pay':
                pay.append(list[1])
            elif list[0]=='workplace':
                workplace.append(list[1])
            elif list[0]=='sex':
                sex.append(list[1])
        if len(education_requirement)== 0:
            education_requirement = ['专科', '本科', '硕士', '博士']
        if len(pay )== 0:
            pay = ['3000-3999', '4000-5999', '6000-7999', '8000-9999', '10000-15000']
        if len(workplace) == 0:
            workplace = ['北京', '上海', '深圳', '天津']
        if len(sex) == 0:
            sex = ['男', '女','不限']
        positions=Position.objects.filter(education_requirement__in=education_requirement,is_delete='0').order_by("-release_time")
        positions = positions.filter(workplace__in=workplace)
        positions = positions.filter(pay__in=pay)
        positions = positions.filter(sex__in=sex)
        paginator = Paginator(positions, pageSize)
        count = paginator.count
        try:
            positions = paginator.page(page)
        except PageNotAnInteger:
            positions = paginator.page(1)
        except EmptyPage:
            positions = paginator.page(paginator.num_pages)
        position_list = serializers.serialize('json', positions)
        return JsonResponse({'status': 'successful', 'position_list': position_list,'total':count})

#企业条件检索求职者简历
def conditionResumeSearch(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        page = request.POST.get('page')
        pageSize = int(request.POST.get('pageSize'))
        condition = request.POST.get('condition')
        print(condition)
        condition=condition.replace('[','').replace(']','').replace('"','').replace('\'','').split(',')
        education_background=[]
        city = []
        sex = []
        hunter_list=[]
        user_list=[]
        resume_list=[]
        #json字符串处理
        for i in condition:
            i=i.replace('{','').replace('}','')
            list=i.split(':')
            if list[0]=='education_background':
                education_background.append(list[1])
            elif list[0]=='city':
                city.append(list[1])
            elif list[0]=='sex':
                if list[1]=='男':
                    sex.append('0')
                elif list[1] == '女':
                    sex.append('1')
        #填充in列表
        if len(education_background)== 0:
            education_background = ['专科', '本科', '硕士', '博士']
        if len(sex) == 0:
            sex = ['0', '1']
        #过滤
        hunters=Hunter.objects.filter(education_background__in=education_background).order_by('id')
        if len(city)== 0:
            pass
        else:
            hunters = hunters.filter(city__in=city)
        hunters = hunters.filter(sex__in=sex)

        for hunter in hunters:
            resume = Resume.objects.filter(hunter_id=hunter.id).first()
            resume_list.append(resume)
            # resume_list=resume_list.order_by('-refresh_time')
            # 逆序
        resume_list.sort(key=lambda t: t.refresh_time, reverse=True)

        paginator = Paginator(resume_list, pageSize)
        count = paginator.count
        print(count)
        try:
            resume_list = paginator.page(page)
        except PageNotAnInteger:
            resume_list = paginator.page(1)
        except EmptyPage:
            resume_list = paginator.page(paginator.num_pages)

        for i in resume_list:
            hunter = Hunter.objects.filter(id=i.hunter_id).first()
            hunter_list.append(hunter)
            user = User.objects.filter(id=hunter.user_id).first()
            user_list.append(user)
        hunter_list = serializers.serialize('json', hunters)
        user_list = serializers.serialize('json', user_list)
        resume_list = serializers.serialize('json', resume_list)
        return JsonResponse({'status': 'successful', 'user_list': user_list, 'resume_list': resume_list,'hunter_list': hunter_list,'tatal':count})


#刷新，并将重新招聘
def refreshReleaseTime(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        id = request.POST.get('id')
        position = Position.objects.filter(id=id).first()
        # 如果没有取到默认设置为none
        # print(request.session.get('refresh',None))
        if  position.release_time==datetime.date.today():
            return JsonResponse({'status': 'warning', 'errs': '每天只限刷新一次'})
        else:
            position.release_time = timezone.now()

            #如果重新招聘，2表示暂停招聘
            if position.is_delete=='2':
                position.is_delete ='0'
            try:
                position.save()
                return JsonResponse({'status': 'successful'})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'warning', 'errs': '刷新失败'})
#企业暂停职位招聘
def pausePosition(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    if request.method == 'POST':
        id = request.POST.get('id')
        position = Position.objects.filter(id=id).first()
        #暂停招聘
        position.is_delete = '2'
        try:
            position.save()
            return JsonResponse({'status': 'successful'})
        except Exception as e:
            logger.warning(f'{e}')
            return JsonResponse({'status': 'warning', 'errs': '暂停失败'})
#负载：统计求职者于企业登录时间断
def loginTime(request):
    if not request.session.get('is_login', None):
        return redirect('/api/login/')
    users=User.objects.filter(user_type__in=['1','2'])
    #创建长度24的list
    count=[0]*24
    times=[]
    for user in users:
        time=user.last_login_time
        times.append(time)
    for time in times:
        #strf返回以可读字符串表示时间
        #20：32：:04转换成203204
        time_int=int(time.strftime("%H%M%S"))
        for i in range(24):
            if i*10000<=time_int<(i+1)*10000:
                count[i]=count[i]+1
    return JsonResponse({'status': 'successful', 'count': count})


def test(request):
    return render(request,'backend/test.html')