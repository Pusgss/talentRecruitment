# from captcha.fields import CaptchaField
from django import forms
from django.core import validators
from django.forms import TextInput, ModelForm
from django.core.cache import cache
from backend.models import User, Resume, WorkExperience, ProjectExperience, EducationExperience, Position, Company, \
    Hunter, Interview, News
from django.forms import widgets as wid #因为重名，所以起个别名

# class LoginForm(forms.Form):
#     user_email = forms.CharField( label="邮箱", widget=TextInput(attrs={'class': 'textinput form-control'}))
#     user_password = forms.CharField(label="密码", max_length=20,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#     # code = forms.CharField(validators=[validators.RegexValidator(r'\d{4}', message='请输入正确格式的验证码！')], label="验证码")
#     # captcha = CaptchaField(label='验证码',error_messages={'invalid':u'验证码错误'})#invalid默认显示英文
#
#     def clean(self):
#         tel = self.cleaned_data.get('user_phone ')
#         if User.objects.filter(user_phone=tel).count() < 0:
#             raise forms.ValidationError(message="此手机号码还没有验证，请检查")
#         return self.cleaned_data
class LoginForm(ModelForm):
    class Meta:
        model=User
        exclude = ['creat_time', 'last_login_time','user_phone','user_type','ip']
class RegisterForm(ModelForm):
    class Meta:
        model = User  # 具体要操作那个模型
        # fields = ['user_name','user_phone', 'user_email', ]  # 允许编辑的字段
        exclude = ['creat_time','last_login_time','ip']
# class RegisterForm(forms.Form):
#     user_name = forms.CharField(label="真实姓名",min_length=2, max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}),error_messages={'requird':'用户名不能为空'})
#     user_password = forms.CharField(label="密码",min_length=6, max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control'}),error_messages={'requird':'密码不能为空'})
#     # user_password2 = forms.CharField(label="确认密码",min_length=6, max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
#
#     # user_type=forms.CharField(label="用户类型",max_length=20,widget=forms.TextInput(attrs={'class': 'form-control'}))
#     user_email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'email'}),error_messages={'required':'邮箱不能为空','invalid':"邮箱格式不对"})
#     user_phone=forms.CharField(validators=[validators.RegexValidator(r'1[345678]\d{9}', message='请输入正确格式的手机号码！')],label="手机号",widget=forms.TextInput(attrs={'id': 'user_phone','onchange':'isPhoneNum()'}))
#     # id_card = forms.CharField(validators=[validators.RegexValidator(r'\d{17}\w{1}', message='请输入正确格式的身份证号码！')],
#     #                           label="身份证号码")
#     # user_type_choices = ((1, '求职者'), (2, '企业'), (3, '管理员'))#前者保存在数据库，后者显示在前端界面
#     user_type= forms.CharField(min_length=2, max_length=3,label='身份',widget=forms.TextInput(attrs={'class': 'form-control'}),error_messages={'requird':'用户名不能为空'})
#     # captcha = CaptchaField(label='验证码')
#     # code = forms.CharField(validators=[validators.RegexValidator(r'^[a-zA-Z0-9]{5}$', message='请输入正确格式的验证码！')], label="验证码")
#     #手机号验证唯一性；
#     #单个字段验证
#     # def clean_user_phone(self):  # 如果你想进一步对字段进行验证  系统自动调用clean_
#     #     user_phone = self.cleaned_data.get('user_phone')
#     #     exists = User.objects.filter(user_phone=user_phone).exists()
#     #     if exists:
#     #         raise forms.ValidationError("此手机号码已认证过,不能重复认证！")
#     #     return user_phone
#
#     # 多个字段验证
#     # def clean(self):
#     #     #以后遇到表单验证中  判断两个字段是否相等
#     #     # 等待验证成功以后再判断这个时候需要重写clean方法  继承于父clean方法
#     #     clean_data = super().clean()
#     #     password = clean_data.get('user_password1')
#     #     repassword = clean_data.get('user_password2')
#     #     user_email=clean_data.get('user_email')
#     #     code = clean_data.get('code')
#     #     cache_code  = cache.get('syl_' + user_email)
#     #     #邮箱验证
#     #     if not cache_code :
#     #         raise forms.ValidationError(message="验证码已失效")
#     #     if cache_code != code:
#     #         raise forms.ValidationError(message="验证码不正确")
#     #     # if User.objects.filter(tel=tel).count() > 0:
#     #     #     raise forms.ValidationError(message="此手机号码已认证过,不能重复认证")
#     #     cache.delete('syl_' + user_email)
#     #     #密码验证
#     #     if  password!= repassword:
#     #         raise forms.ValidationError(message="两次密码不一致")
#     #     return clean_data

#用户显示
class UserForm(ModelForm):
    class Meta:
        model = User  # 具体要操作那个模型
        # fields = ['user_name','user_phone', 'user_email', ]  # 允许编辑的字段
        exclude = ['creat_time','user_type','user_password','last_login_time' ,'ip']
        # widgets={
        #     'user_password': forms.PasswordInput(),
        #     'user_type':forms.RadioSelect(),
        #
        # }
# class ResumeForm(forms.Form):
#     sex_choices = (('m', '男'), ('f', '女'))
#     sex = forms.CharField(min_length=4,max_length=6, label='性别',widget=forms.Select(choices=sex_choices),initial='男')
#     birthday = forms.CharField(max_length=32, label='生日')
#     city = forms.CharField(max_length=32, label='所在城市', error_messages={
#    "required": "不能为空",
#    "invalid": "格式错误",
#    "min_length": "用户名最短8位"
#   })
#     Correspondence_address = forms.CharField(max_length=32, label='通讯地址')
#     registered_permanent_residence = forms.CharField(max_length=32, label='户口所在地')
#     education_backend_choices = (('大专', '大专'), ('本科', '本科'), ('硕士', '硕士'), ('博士', '博士'), ('其他', '其他'))
#     education_background = forms.CharField( label='学历', widget=forms.Select(choices=education_backend_choices),initial='')
#     # upload_to图片保存在该路径下, #上传的文件保存到MEDIA_root +upload_to后的路径
#     qq = forms.CharField(max_length=32, label='qq')
#     # photo = forms.ImageField(upload_to='img', label="头像")
#     exprctrd_work_city = forms.CharField(max_length=32, label='期望工作地点')
#     desired_position = forms.CharField(max_length=32, label='期望职位')
#     expected_salary = forms.CharField(max_length=32, label='期望薪资')
#     self_assessment = forms.CharField(max_length=32, label='自我评价',widget=forms.Textarea,initial='本人热爱工作')
class ResumeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['self_assessment'].initial='本人热爱工作'
        # self.fields['comment'].widget.attrs.update(size='40')
    class Meta:
        model=Resume
        exclude=['refresh_time','hunter','companys','temp']
        labels={
        }
        widgets = {
            "self_assessment": wid.Textarea(attrs={"class": "c1"})  # 还可以自定义属性
        }
        error_messages = {
            'photo': {
                'invalid_image': '请上传正确格式的图片！'
            }
        }


class EducationExperienceForm(ModelForm):
    class Meta:
        model=EducationExperience
        field=['id','school_name',
    'enrollment_time',
    'graduation_time',
    'education_background',
    'major',
    'honor',]
        exclude=['resume',]
class WorkExperienceForm(ModelForm):
    class Meta:
        model=WorkExperience
        exclude=['resume',]
class ProjectExperienceForm(ModelForm):
    class Meta:
        model=ProjectExperience
        exclude=['resume',]
        # exclude = ['resume', 'user']
class ModifyPwdForm(ModelForm):
    class Meta:
        model=User
        fields = ['user_password', 'user_email' ]
    # password1 = forms.CharField(required=True, min_length=5)
    # password2 = forms.CharField(required=True, min_length=5)
    # code = forms.CharField(validators=[validators.RegexValidator(r'^[a-zA-Z0-9]{5}$', message='请输入正确格式的验证码！')], label="验证码")
    # def clean(self):
    #     #以后遇到表单验证中  判断两个字段是否相等
    #     # 等待验证成功以后再判断这个时候需要重写clean方法  继承于父clean方法
    #     clean_data = super().clean()
    #     password = clean_data.get('user_password1')
    #     repassword = clean_data.get('user_password2')
    #     user_email=clean_data.get('user_email')
    #     code = clean_data.get('code')
    #     cache_code  = cache.get('syl_' + user_email)
    #     #邮箱验证
    #     if not cache_code :
    #         raise forms.ValidationError(message="验证码已失效")
    #     if cache_code != code:
    #         raise forms.ValidationError(message="验证码不正确")
    #     # if User.objects.filter(tel=tel).count() > 0:
    #     #     raise forms.ValidationError(message="此手机号码已认证过,不能重复认证")
    #     cache.delete('syl_' + user_email)
    #     #密码验证
    #     if  password!= repassword:
    #         raise forms.ValidationError(message="两次密码不一致")
    #     return clean_data
class CompanyForm(ModelForm):
    class Meta:
        model=Company
        exclude=['user','status']
class HunterForm(ModelForm):
    class Meta:
        model=Hunter
        exclude=['user','photo',]
class PositionForm(ModelForm):
    class Meta:
        model=Position
        exclude=['company','company_name','hunters','is_delete','release_time']
class InterviewForm(ModelForm):
    class Meta:
        model=Interview
        fields=['time','title','content']
        widgets = {
          'time': forms.DateTimeInput(format=('%Y-%m-%d %H:%M:%S'), attrs={"type": 'date'}),
       }
class NewsForm(ModelForm):
    class Meta:
        model=News
        fields=['time','title','content']
        widgets = {
          'time': forms.DateTimeInput(format=('%Y-%m-%d %H:%M:%S'), attrs={"type": 'date'}),
       }