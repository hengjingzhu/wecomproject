from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files import File


from apimessage.celery_settings import app
from apimessage.models import *

from tools.openai_response_chatgpt import OpenAIModel
from tools.wecom_tools import WECOMM
from tools.config import *
from tools.audio_to_MP3 import convert_amr_to_mp3

from datetime import datetime

import uuid

import os


# os.environ.setdefault('DJANGO_SETTINGS_MODULE','wecom.local_settings')   #告诉celery 把django的指定项目融合,所以用的这个项目的settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE','wecom.production_settings')

# 设置环境变量来确保不使用代理
os.environ['NO_PROXY'] = settings.AWS_S3_ENDPOINT_URL
os.environ['no_proxy'] = settings.AWS_S3_ENDPOINT_URL



general_text_reply_prompt_template = GENERAL_TEXT_REPLY_PROMPT_TEMPLATE


# 保存图片到 minio
@app.task
def async_save_image_to_minio(
                        from_user_name,
                        media_id,
                        agent_id,
                        create_time):
    
    
    
    response_content = '图片收到'
        
    # 使用 wecom_tools的工具下载图片
    response = WECOMM(agentId=agent_id).Get_media_data(media_id=media_id)
    # response.raise_for_status()  # 确保请求成功

    # 创建一个新的 MyImageModel 实例
    media_instance = MyStaticModel()
    
    # 生成一个唯一的UUID字符串
    unique_id = uuid.uuid4().hex
    new_media_name = from_user_name+'_'+create_time+'_'+unique_id
    
    media_instance.username = from_user_name
    media_instance.agent_id_id = agent_id
    
    # 使用 Django 的 ContentFile 将图片内容保存到 ImageField
    media_instance.image.save(f'{from_user_name}/{new_media_name}.jpeg', ContentFile(response), save=True)
    
    # print('保存的图片地址为',media_instance.image)
    # 组织发送消息的data
    data={
            "touser" : from_user_name,
            "msgtype" : 'text',
            "agentid" : agent_id,
            "text" : {
                "content" : response_content
            },
        }
    # 把反馈消息推送到用户的企业微信
    result = WECOMM(agentId=agent_id).send_message(data=data)
    print('celery 执行结果',result)
    return result

# 保存视频到minio
@app.task
def async_save_video_to_minio(
                        from_user_name,
                        media_id,
                        agent_id,
                        create_time):
    
    response_content = '视频收到'
        
    # 使用 wecom_tools的工具下载图片
    response = WECOMM(agentId=agent_id).Get_media_data(media_id=media_id)
    # response.raise_for_status()  # 确保请求成功

    # 创建一个新的 MyImageModel 实例
    media_instance = MyStaticModel()
    new_media_name = from_user_name+'_'+create_time
    
    media_instance.username = from_user_name
    media_instance.agent_id_id = agent_id
    
    # 使用 Django 的 ContentFile 将图片内容保存到 ImageField
    media_instance.video.save(f'{from_user_name}/{new_media_name}.mp4', ContentFile(response), save=True)
    
    # print('保存的图片地址为',media_instance.image)
    # 组织发送消息的data
    data={
            "touser" : from_user_name,
            "msgtype" : 'text',
            "agentid" : agent_id,
            "text" : {
                "content" : response_content
            },
        }
    # 把反馈消息推送到用户的企业微信
    result = WECOMM(agentId=agent_id).send_message(data=data)
    print('celery 执行结果',result)
    return result


# gpt 回复
@app.task
def async_send_messages_through_gpt(message_type,
                                    received_message,
                                    from_user_name,
                                    agent_id,
                                    chat_bot_config,
                                    event
                                    ):
    
    
    # 把 gpt 的参数拿出来
    #  <class 'dict'> {'agent_id': 1000002, 'agent_name': 'chatbot2', 'llm_model_name': 'claude-3-haiku-20240307', 
    # 'system_prompt': 'you are a helpful ai', 'user_prompt': '', 'temperature': Decimal('0.0'), 'max_token_response': 5000, 'is_active': True}
    GPT_Model_Name = chat_bot_config['llm_model_name']
    GPT_System_Prompt = chat_bot_config['system_prompt']
    GPT_User_Prompt = chat_bot_config['user_prompt']
    GPT_Temperature = float(chat_bot_config['temperature'])
    GPT_Max_Token_Response = chat_bot_config['max_token_response']
    
    user_message = GPT_User_Prompt+received_message
    # print('user_message',user_message)
    # 在数据库中查找当天有没有聊天记录,历史记录是一个人一天来记录的，如果当天有历史记录就取出来，如果没有就新增一条
    now = datetime.now()
    print('现在时间是',now,type(now))
    history_message_queryset = GENERALBLACKBOX.objects.filter(updated_time__date=now.today(),username=from_user_name,agent_id_id=agent_id)
    
    history_message_list_to_GPT = []
    # 数据库的历史数据是这样的[{"role":"user","content":"question",msg_type:"text","create time":"datetime"},....]
    if history_message_queryset:
        history_message_obj = history_message_queryset.order_by('updated_time').last()
        history_message_from_DB = history_message_obj.messages
        
        
        
        print('今天的历史记录history_message_from_DB',history_message_from_DB)
        # 取历史记录中最后12个,作为历史消息发送给GPT
        for item in history_message_from_DB[-12:]:
            temp_dict = {
                'role':item['role'],
                'content':item['content']
            }
            history_message_list_to_GPT.append(temp_dict)
            
        
    # 没有找到历史记录，就是一条新的对话框。    
    if not history_message_queryset:
        print('今天没有历史记录，是一个全新的对话')
        history_message_from_DB = []
        history_message_list_to_GPT = []
        history_message_obj = GENERALBLACKBOX()
    
    history_message_from_DB.append({'role':'user','content':user_message,'msg_type':message_type,'create time':now.isoformat()})
    print('history_message_from_DB',history_message_from_DB)
    
    """先把用户的消息存储起来，然后发送给openai等回复
    """    
    OpenAIObj = OpenAIModel(
                            user=from_user_name,
                            user_query = user_message,
                            agent_id = agent_id,
                            open_ai_model_name=GPT_Model_Name,
                            model_temperature=GPT_Temperature,
                            max_token_response=GPT_Max_Token_Response,
                            )
    # print(OpenAIObj.reply_message('你好',start_messages))
   
    GPT_response = OpenAIObj.reply_message(user_message,start_messages=history_message_list_to_GPT,system_role_description=GPT_System_Prompt)
    print(GPT_response)
    response_content = GPT_response[0]
    print(response_content)
        
        
    # 组织发送给用户消息的data
    data={
            "touser" : from_user_name,
            "msgtype" : 'text',
            "agentid" : agent_id,
            "text" : {
                "content" : response_content
            },
    }
    # 把消息推送到用户的企业微信
    result = WECOMM(agentId=agent_id).send_message(data=data)
    print(result)
   
    # 发送完毕后,把gpt回复的信息放到history_message_from_DB中存回给数据库
    now = datetime.now()
    history_message_obj.username = from_user_name
    history_message_obj.corp_id = settings.CORPID
    history_message_obj.event = event
    history_message_obj.agent_id_id = agent_id
    history_message_from_DB.append({'role':'assistant','content':response_content,'msg_type':message_type,'create time':now.isoformat()})
    history_message_obj.messages = history_message_from_DB
    history_message_obj.save()

    return result # 把结果保存到backend_url中



# 保存音频到minio,并且使用 whisper转为文字
@app.task
def async_save_voice_to_minio(msg_type,
                        from_user_name,
                        media_id,
                        agent_id,
                        create_time,
                        chat_bot_config,
                        event='general'):
    
    
      
    """下载音频文件,把音频转为mp3格式
    """
    response = WECOMM(agentId=agent_id).Get_voice_data(media_id=media_id)
    
    mp3_stream = convert_amr_to_mp3(response)


    """保存音频到minio
    """  
    # 创建一个新的 MyImageModel 实例
    media_instance = MyStaticModel()
    new_media_name = from_user_name+'_'+create_time
    
    media_instance.username = from_user_name
    media_instance.agent_id_id = agent_id
    
    # 使用 Django 的 File 将内容保存到 voice 的 ImageField
    media_instance.voice.save(f'{from_user_name}/{new_media_name}.mp3', File(mp3_stream), save=True)
    
    
    print(media_instance.voice.url)
    """使用 whisper转为文字
        voice_words返回的是听到的字符串
    """
    # 上传的文件格式,这里需要满足如下条件 a tuple of (filename, contents, media type).
    uploaded_audio_file = (media_instance.voice.name,mp3_stream.getvalue(),'mp3')
    voice_words = OpenAIModel(open_ai_model_name="whisper-1",user=from_user_name,
                            user_query = 'None',
                            agent_id = agent_id,).stt_whisper(audio_file=uploaded_audio_file)
    
    
    """把音频消息回复给到 gpt 生成回复答案。并且回复消息给到客户
    """
    # 组织发送反馈消息的data
    result = async_send_messages_through_gpt(message_type=msg_type,
                                    received_message=voice_words,
                                    from_user_name=from_user_name,
                                    agent_id=agent_id,
                                    chat_bot_config=chat_bot_config,
                                    event=event
                                    )
    """回复信息给到用户
    """
    # response_content = voice_words
    # data={
    #         "touser" : from_user_name,
    #         "msgtype" : 'text',
    #         "agentid" : agent_id,
    #         "text" : {
    #             "content" : response_content
    #         },
    #     }
    # # 把反馈消息推送到用户的企业微信
    # result = WECOMM(agentId=agent_id).send_message(data=data)
    print('celery 执行结果',result)
    return result