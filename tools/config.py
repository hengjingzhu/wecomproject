import os
import django
print(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wecom.local_settings')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','wecom.production_settings')
django.setup()


from django.conf import settings



# 用来存储 access token,redis database config
REDIS_EXTERNAL_HOST = settings.REDIS_EXTERNAL_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_DATABASE = '1'


# we comm config
CORPID = settings.CORPID
WECOM_CHAT_BOT_CORPSECRET = settings.WECOM_CHAT_BOT_CORPSECRET

# token and aes key for receive message.
RECEIVE_MESSAGE_TOKEN = settings.RECEIVE_MESSAGE_TOKEN
ENCODING_AES_KEY = settings.ENCODING_AES_KEY


# openai config

SECRETKEY = settings.OPENAI_SECRETKEY
ORG_ID = settings.OPENAI_ORG_ID


OPEN_AI_MODEL_NAME = 'gpt-3.5-turbo'
# max token in one response
MAX_TOKEN_RESPONSE = 2500
# chatgpt temperature 
MODEL_TEMPERATURE = 0
# set max_token_inmessage, long conversation
MAX_TOKEN_INMESSAGE = 15000
# GPT RESPONSE PROMPT
GENERAL_TEXT_REPLY_PROMPT_TEMPLATE = '你会先自我介绍，你的名字叫 CyberDavid'


# claude config
ANTHROPIC_SECRETKEY = settings.ANTHROPIC_SECRETKEY

