from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
from django.contrib.auth.models import AbstractUser

from decimal import Decimal


# class UserInfo(AbstractUser):  #继承AbstractUser, 添加原来User 没有的字段即可，其他的都是继承过来了
#     """用户模型类"""
#     phone = models.CharField(max_length=11, verbose_name='手机号码', blank=True, null=True, unique=True)
    
#     def __str__(self):
#         return self.username
 
#     class Meta:
#         # 联合索引,联合同步查询，提高效率
#         db_table = 'auth_user'
#         index_together = ["username", "phone"]
#         verbose_name='用户'
#         verbose_name_plural=verbose_name


class MyStaticModel(models.Model):
    
    username = models.CharField('用户名',max_length=255,null=True,blank=True)
    agent_id = models.ForeignKey('BOT_LLM_CONFIG',on_delete=models.DO_NOTHING,to_field='agent_id',null=True,blank=True)
    image = models.ImageField(upload_to='images/',null=True,blank=True)
    video = models.ImageField(upload_to='video/',null=True,blank=True)
    voice = models.ImageField(upload_to='voice/',null=True,blank=True)
    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)

# LLM bot configration
class BOT_LLM_CONFIG(models.Model):
    
    LLM_CHOICES = [
        ('OpenAI', (
                ('gpt-3.5-turbo', 'gpt-3.5-turbo'),
                ('gpt-4-turbo', 'gpt-4-turbo'),
            )
        ),
        ('Claude', (
                ('claude-3-haiku-20240307', 'claude-3-haiku-20240307'),
                ('claude-3-sonnet-20240229', 'claude-3-sonnet-20240229'),
                ('claude-3-opus-20240229', 'claude-3-opus-20240229'),
            )
        ),
    ]
    
    agent_id = models.IntegerField("bot企业微信代码",unique=True)
    agent_name = models.CharField('bot名字',max_length=255)
    # 给agent 配置的 LLM
    llm_model_name = models.CharField('LLM Model Name',choices = LLM_CHOICES,default='gpt-3.5-turbo',max_length=255)
    system_prompt = models.TextField('LLM System Prompt',default = 'you are a helpful ai')
    user_prompt = models.TextField("LLM User Prompt",null = True,blank = True)
    temperature = models.DecimalField('LLM Temperature',max_digits = 2,decimal_places = 1,default = 0,
                                      validators=[MinValueValidator(Decimal('0')),
                                            MaxValueValidator(Decimal('1.0'))]
                                      )
    max_token_response = models.IntegerField('LLM Max Token Return',default=4000)

    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)

    def __str__(self):
        return str(self.agent_id)

    class Meta:
        
        verbose_name='机器人配置'
        verbose_name_plural=verbose_name

# 通用聊天机器人对话历史
class GENERALBLACKBOX(models.Model):
    
    username = models.CharField('用户名',max_length=255)
    corp_id = models.CharField("企业微信corpid",max_length=255)
    # 事件:是直接聊，还是客服事件
    event = models.CharField("事件",max_length=255)
    # 微信机器人id
    agent_id = models.ForeignKey('BOT_LLM_CONFIG',on_delete=models.DO_NOTHING,to_field='agent_id')
    
    
    # {role:''user',content:''hello',created_time:'2024.01.01 12:12:00',msg_type:'text'}
    messages = models.JSONField("对话内容")
    
    created_time = models.DateTimeField('创建时间',auto_now_add=True)
    updated_time = models.DateTimeField('更新时间',auto_now=True)
    is_active = models.BooleanField('是否活跃',default=True)
    
    
    class Meta:
        # 联合索引,联合同步查询，提高效率
        #db_table = 'auth_user'
        #index_together = ["username", "phone"]
        verbose_name='General Blackbox'
        verbose_name_plural=verbose_name