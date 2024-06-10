"""
Django settings for wecom project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apimessage',
    'storages'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wecom.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRESQL_INTERNAL_DBNAME'),
        'USER': os.environ.get('POSTGRESQL_INTERNAL_USERNAME'),
        'PASSWORD': os.environ.get('POSTGRESQL_INTERNAL_PASSWORD'),
        'HOST': os.environ.get('POSTGRESQL_INTERNAL_HOST'),                    
        'PORT': os.environ.get('POSTGRESQL_INTERNAL_PORT'),
        'client_encoding':'UTF8',
        'default_transaction_isolation':'read committed',
        'OPTIONS': {
            'options': '-c search_path="wecom"'   # 指定PostgreSQL 的 Schema,如果是大写要加上双引号
        }
    }
}

# 用来存储 access token,redis database config
REDIS_EXTERNAL_HOST = os.environ.get('REDIS_INTERNAL_HOST')
REDIS_PORT = '6379'
REDIS_PASSWORD = os.environ.get('REDIS_INTERNAL_PASSWORD')

CACHES = {
    "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{REDIS_EXTERNAL_HOST}:{REDIS_PORT}/2",		#数字代表使用redis哪个数据库
                            "OPTIONS": 
                            {
                                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                                "PASSWORD": f"{REDIS_PASSWORD}",
                            }
                }
    }



# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # 注册自定义用户模型，格式：“app应用名.表名称”
# AUTH_USER_MODEL = 'apimessage.UserInfo'

STATICFILES_DIRS = [
    				BASE_DIR / "static",
   					#应用名下面的static文件夹
    				'apimessage/static/',
    				]

# we comm config
CORPID = os.environ.get('WECOM_CORPID')

# token and aes key for receive message.
RECEIVE_MESSAGE_TOKEN = os.environ.get('WECOM_RECEIVE_MESSAGE_TOKEN')
ENCODING_AES_KEY = os.environ.get('WECOM_ENCODING_AES_KEY')

# self build we com bot corpsecret,"agentID":"CORPSECRET"
WECOM_CHAT_BOT_CORPSECRET = os.environ.get('WECOM_CHAT_BOT_CORPSECRET')


# openai config
OPENAI_SECRETKEY = os.environ.get('OPENAI_SECRETKEY')
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')


# claude 配置
ANTHROPIC_SECRETKEY = os.environ.get('ANTHROPIC_SECRETKEY')

# MinIO 配置
# MinIO storage settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'wecom'
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_USE_SSL = False
# AWS_LOCATION = 'yourBucketSubdirectory'  # 可选，如果想在存储桶内使用子目录

# 使用S3作为Django的默认文件存储机制
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
