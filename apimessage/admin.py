from django.contrib import admin
from django.forms import widgets
from django.core.cache import cache

from django.forms.models import model_to_dict

from apimessage.models import *

import time

admin.site.site_header = '企业微信管理后台'
admin.site.site_title = '企业微信管理后台'
admin.site.index_title = '企业微信index_title'
# Register your models here.

@admin.register(BOT_LLM_CONFIG)
class BOT_LLM_CONFIG_Admin(admin.ModelAdmin):
    # 如果是外键的话，会在前端显示 外键中模型中 def __str__ 的返回值
    # 可以自定义字段名
    list_display = ['agent_id','agent_name','llm_model_name','created_time','updated_time']
    
    # 控制list_display中的字段,点击哪一个字段可以进入到修改数据的修改页.
    list_dispay_links = ['agent_id','agent_name']
    
    # 添加过滤器,过滤器自动根据设置的字段名分组,可以使用
    list_filter = ['agent_id','agent_name']
    
    # 添加搜索框，会在设置的字段名模糊查询
    search_fields = ['agent_id','agent_name','llm_model_name']
    
    
    # 每页显示多少条
    list_per_page = 30
    
    # 显示时间分组数据
    date_hierarchy = 'updated_time'
    
    def save_model(self, request, obj, form, change):
        
        
        # {'agent_id': 1000002, 'agent_name': 'chatbot2', 'llm_model_name': 'gpt-3.5-turbo', 'system_prompt': 'you are a helpful ai', 'user_prompt': '', 'temperature': Decimal('0.0'), 'max_token_response': 5000, 'is_active': True}
        # <class 'dict'>
        frontend_formdata = form.cleaned_data
        # print(frontend_formdata)

        super().save_model(request, obj, frontend_formdata, change)

    def save_related(self,request, form, formsets,change):
        
        # {'agent_id': 1000002, 'agent_name': 'chatbot2', 'llm_model_name': 'gpt-3.5-turbo', 'system_prompt': 'you are a helpful ai', 'user_prompt': '', 'temperature': Decimal('0.0'), 'max_token_response': 5000, 'is_active': True}
        # <class 'dict'>
        frontend_formdata = form.cleaned_data
        agent_id = frontend_formdata['agent_id']
        # print(form.cleaned_data,type(form.cleaned_data),change)
        
        #   把模型的数据存储到 redis的缓存, key是 agent_id
        save_result = cache.set(agent_id,frontend_formdata,timeout=None)
        # print('bot_llm_config save_result',save_result)
        
        # 如果保存失败，那就重新尝试5次
        retry_time = 0
        max_retry_time = 5
        if not save_result:
            while retry_time<=max_retry_time and not save_result:
                print(f"this is {retry_time} time to try set bot_llm_config into redis")
                time.sleep(1)
                save_result = cache.set(agent_id,frontend_formdata,timeout=None)
                retry_time+=1
                
        
        super().save_related(request, form, formsets, change)
    
    def delete_model(self,request, obj):
        print('delete this model')
        # 只有超级用户才能删除
        agent_id = obj.agent_id
        if request.user.is_superuser:
            obj.delete()
            # 删除缓存数据
            delete_result = cache.delete(agent_id)
            print('delete agent_id',delete_result)
            
            # 如果删除失败，那就重新尝试5次
            retry_time = 0
            max_retry_time = 5
            if not delete_result:
                while retry_time<=max_retry_time and not delete_result:
                    print(f"this is {retry_time} time to try delete {agent_id} into redis")
                    time.sleep(1)
                    delete_result = cache.delete(agent_id)
                    retry_time+=1
            
            
    def delete_queryset(self,request, queryset):
        print('delete queryset',queryset)
        # 只有超级用户才能删除
        if request.user.is_superuser:
            # 删除缓存数据
            agent_id_list = []
            for obj in queryset:
                # print('obj',obj.agent_id)
                agent_id_list.append(obj.agent_id)
            # print(agent_id_list)
            delete_result = cache.delete_many(agent_id_list)

            # 如果删除失败，那就重新尝试5次
            retry_time = 0
            max_retry_time = 5
            if not delete_result:
                while retry_time<=max_retry_time and not delete_result:
                    print(f"this is {retry_time} time to try delete {agent_id_list} into redis")
                    time.sleep(1)
                    delete_result = cache.delete_many(agent_id_list)
                    retry_time+=1

            # 删除数据库数据
            queryset.delete()

@admin.register(GENERALBLACKBOX)
class GENERAL_BLACKBOX_Admin(admin.ModelAdmin):
    # 如果是外键的话，会在前端显示 外键中模型中 def __str__ 的返回值
    # 可以自定义字段名
    list_display = ['username','event','agent_id','created_time','updated_time']
    
    # 控制list_display中的字段,点击哪一个字段可以进入到修改数据的修改页.
    list_dispay_links = ['username','event']
    
    # 添加过滤器,过滤器自动根据设置的字段名分组,可以使用
    list_filter = ['username','event','agent_id']
    
    # 添加搜索框，会在设置的字段名模糊查询
    search_fields = ['username','event','agent_id']
    
    
    # 每页显示多少条
    list_per_page = 30
    
    # 显示时间分组数据
    date_hierarchy = 'updated_time'

    # 自定义 jsonfield 的显示大小
    formfield_overrides = {
        models.JSONField: {'widget': widgets.Textarea(attrs={'rows': 40, 'cols': 150})},
    }