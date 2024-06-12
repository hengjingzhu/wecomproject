from celery import Celery
from django.conf import settings
import os
from tools.config import REDIS_EXTERNAL_HOST,REDIS_PASSWORD,REDIS_PORT

# os.environ.setdefault('DJANGO_SETTINGS_MODULE','wecom.local_settings')   #告诉celery 把django的指定项目融合,所以用的这个项目的settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','wecom.production_settings')

# 初始化celery对象
app = Celery('gptresponse')
#配置celery
app.conf.update(
    broker_url = f'redis://:{REDIS_PASSWORD}@{REDIS_EXTERNAL_HOST}:{REDIS_PORT}/1',  		# 设置celery 的消息传输中间件，指定redis数据库1号数据库,用来当作worker拿任务的地方
    result_backend = f'redis://:{REDIS_PASSWORD}@{REDIS_EXTERNAL_HOST}:{REDIS_PORT}/2 ',    # 把worker的执行结果存储到2号仓库里
	result_expires = 180								                                    # 设置结果过期时间，单位秒
    )

#让celery这个对象，自己在这个项目下的settings.py中各个注册的app应用取寻找worker装饰器函数
app.autodiscover_tasks(settings.INSTALLED_APPS)