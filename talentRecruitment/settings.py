"""
Django settings for talentRecruitment project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
#coding=utf8
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys
from importlib import reload

from django.http import request
from .celeryconfig import *  # 导入Celery配置信息
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ngsl4q4$h!o(jth9^e*dlgesca+qd@ogfp_4^1qe@63^q^!mor'

# SECURITY WARNING: don't run with debug turned on in production!
# settings.debug会导致内存泄漏，请不要在生产环境中使用此设置！所以我们就要在settings配置文件中把debug改为False


DEBUG = True
#允许ip访问
ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [

    'backend',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',#启动session
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'captcha',
    'djcelery',  # 注册celery




]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',#启动session
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'talentRecruitment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'talentRecruitment.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',#引擎
        'HOST': '127.0.0.1',
        'NAME': 'talent',#数据库名
        'USER': 'root',
        'PASSWORD': 'root',


    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
#语言设置：选择中国
LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

#图片
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/../static/../media').replace('\\', '/')     #设置静态文件路径为主目录下的media文件夹
MEDIA_URL = '/media/'
#jquery文件
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),

                    ]
#设置项是否开启URL访问地址后面不为/跳转至带有/的路径
# APPEND_SLASH=True
##############################send_mail####################################
#发送邮件
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.qq.com'#SMTP地址
EMAIL_PORT=25  #端口号
EMAIL_HOST_USER='1115152483@qq.com' #邮箱
EMAIL_HOST_PASSWORD='jwldmznqzylxhjac'#授权码
#是否启动TLS链接(安全链接)。默认是false
EMIAL_USE_TLS = False
EMAIL_FROM='1115152483@qq.com' #发件人邮箱


# redis配置文件
CACHES = {
     "default": {
         "BACKEND": "django_redis.cache.RedisCache",#缓存到redis
         "LOCATION": "redis://127.0.0.1:6379",
         "OPTIONS": {
             "CLIENT_CLASS": "django_redis.client.DefaultClient",
             "CONNECTION_POOL_KWARGS": {"max_connections": 100}
             # "PASSWORD": "密码",
         }
     }
}

SESSION_SAVE_EVERY_REQUEST = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True # 关闭浏览器，则COOKIE失效
SESSION_COOKIE_AGE = 60 * 30 # 30分钟

USE_L10N = False
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'


########################celery settings##############################
# celery中间人 redis://redis服务所在的ip地址:端口/数据库号
BROKER_URL = 'redis://localhost:6379/0'
# celery结果返回，可用于跟踪结果
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# celery内容等消息的格式设置
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# celery时区设置，使用settings中TIME_ZONE同样的时区
CELERY_TIMEZONE = TIME_ZONE

###################日志#####################################

# 创建日志的路径 以/进行路径拼接
LOG_PATH = os.path.join(BASE_DIR, 'log')
# 如果地址不存在，则自动创建log文件夹
if not os.path.join(LOG_PATH):
    os.mkdir(LOG_PATH)

LOGGING = {
    # version只能为1,定义了配置文件的版本，当前版本号为1.0
    "version": 1,
    # True表示禁用logger
    "disable_existing_loggers": False,
    # 格式化
    'formatters': {
        'default': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s][%(funcName)s][%(lineno)d] > %(message)s '
        },
        'simple': {
            'format': '[%(levelname)s][%(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'stu_handlers': {
            'level': 'DEBUG',
            # 日志文件指定为5M, 超过5m重新命名，然后写入新的日志文件
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            'maxBytes': 5 * 1024,
            # 指定文件地址
            'filename': '%s/log.txt' % LOG_PATH,
            'formatter': 'default',
            'encoding': 'utf-8',  # 设置默认编码，否则打印出来汉字乱码
        },
        'uauth_handlers': {
            'level': 'DEBUG',
            # 日志文件指定为5M, 超过5m重新命名，然后写入新的日志文件
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            'maxBytes': 5 * 1024 * 1024,
            # 指定文件地址
            'filename': '%s/uauth.txt' % LOG_PATH,
            'formatter': 'simple'
        }
    },
    'loggers': {
        'stu': {
            'handlers': ['stu_handlers'],
            'level': 'WARNING'
        },
        'auth': {
            'handlers': ['uauth_handlers'],
            'level': 'INFO'
        }
    },

    'filters': {

        }
}


