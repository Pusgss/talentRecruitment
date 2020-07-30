"""talentRecruitment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from django.urls import path
from django.contrib import admin
from django.urls import include
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
import backend.urls
#命名空间
app_name='backend'
urlpatterns = [
    # path('admin/', admin.site.urls),
    #r防止字符转移
    #函数 include() 允许引用其它 URLconfs。每当 Django 遇到 :func：~django.urls.include 时，它会截断与此项匹配的 URL 的部分，并将剩余的字符串发送到 URLconf 以供进一步处理。
    url(r'^admin/',admin.site.urls),
    url(r'^api/',include(backend.urls)),
    url(r'captcha/', include('captcha.urls')) ,  #增加这一行
    url(r'^favicon.ico$',RedirectView.as_view(url=r'/static/favicon.ico',permanent=True)),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)#这句话是用来指定和映射静态文件的路径
# handler500 = 'backend.views.page_error'