from django.views import View
from django.http import request, JsonResponse,HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django.forms.models import model_to_dict


import xml.etree.ElementTree as ET

from apimessage.celery_tasks import async_send_messages_through_gpt,async_save_image_to_minio,async_save_video_to_minio,async_save_voice_to_minio


from tools.urlverify import check_signature,decrypt_echostr,generate_signature,encrypt_message
from tools.time_converter import timestamp_to_datetime_str
from tools.config import RECEIVE_MESSAGE_TOKEN,ENCODING_AES_KEY,CORPID
from tools.openai_response_chatgpt import OpenAIModel

from apimessage.models import *

import time
import json






# Create your views here.
class RECEIVE_MESSAGE(View):
    
    
    
    # get 请求用来填写校验 Receive messages api的时候使用
    def get(self,request):
        print('get',request.GET)
        # 获取GET请求的参数
        msg_signature = request.GET.get('msg_signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        # 验证签名
        if not check_signature(RECEIVE_MESSAGE_TOKEN, timestamp, nonce, echostr, msg_signature):
            print("Signature verification failed")
            return HttpResponse("Signature verification failed", status=403)
        
        # 解密echostr
        try:
            decrypted_echostr = decrypt_echostr(ENCODING_AES_KEY, echostr)
            print('decrypted_echostr',decrypted_echostr)
            return HttpResponse(decrypted_echostr)
        except Exception as e:
            print('Decryption failed',e)
            return HttpResponse("Decryption failed", status=500)
       
    
    # 接受消息并且返回
    def post(self,request):
        
        # 解析GET参数
        msg_signature = request.GET.get('msg_signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        
        # 解析XML数据
        xml_data = ET.fromstring(request.body)
        encrypt = xml_data.find('Encrypt').text
        
        # 解密消息
        decrypted_message = decrypt_echostr(ENCODING_AES_KEY, encrypt)
        # 处理解密后的消息（这里简化处理，实际上需要根据业务逻辑来）
        print('消息接收是:',decrypted_message)
        decrypted_message_xml = ET.fromstring(decrypted_message)
        
        # 先判断下是不是客服事件,如果不是客服事件，就是普通一对一聊天
        # 如果是客服时间会有 Event 标签，事件名称是 kf_msg_or_event
        try:
            message_event_xml = decrypted_message_xml.find('Event').text
            if message_event_xml == 'kf_msg_or_event':
                print('这里开始是客服接管事件')
                # 客服对话逻辑
                
        except AttributeError as e:
            print('decrypted_message_xml',decrypted_message_xml)
            event ='general'
            # 这里就不是客服事件，属于普通一对一聊天事件, 代号是 general
            # 普通表情或文字的 msg_type 是 text, 有 Content 这个标签，里面是 文字
            # 图片或者动图表情，msg_type 是 image, 有PicUrl 标签，里面是 https 图片链接
            # 如果是音频文件的话 ,msg_type 是 voice, 内容是MediaId 这个标签<MediaId><![CDATA[1SlIJxUMDph-hau5Qk99mjOWCrcBTeeZioEPNAf4BeHyhUAWyssnN_tFlQkSkNtKa]]></MediaId>
            # 如果是视频文件的话 ,msg_type 是 video, 内容是MediaId 这个标签<MediaId><![CDATA[1SlIJxUMDph-hau5Qk99mjOWCrcBTeeZioEPNAf4BeHyhUAWyssnN_tFlQkSkNtKa]]></MediaId>
        
            # 1. 先判断下msg_type是 text,image,video,audio
            msg_type = decrypted_message_xml.find('MsgType').text
            
            
            
            # 如果是 发送的是 text 
            if msg_type == 'text':
                # 这里的 tousername 是 corpid,from username 才是发信人
                to_user_name = decrypted_message_xml.find('ToUserName').text
                from_user_name = decrypted_message_xml.find('FromUserName').text
                agent_id = decrypted_message_xml.find('AgentID').text
                create_time = decrypted_message_xml.find('CreateTime').text
                msg_type = decrypted_message_xml.find('MsgType').text
                msg_id = decrypted_message_xml.find('MsgId').text
                message_content = decrypted_message_xml.find('Content').text
                
                print('to_user_name',to_user_name)
                print('agent_id',agent_id)
                print('from_user_name',from_user_name)
                
                # create_time 是 2024-03-26 03:13:30 字符串
                print('create_time',timestamp_to_datetime_str(int(create_time)))
                print('msg_type',msg_type)
                print('msg_id',msg_id)
                print('message_content',message_content)
            
            
            
            
                # 先缓存里查找bot配置信息,如果没有就去数据库里查找
                # {'agent_id': 1000002, 'agent_name': 'chatbot2', 'llm_model_name': 'gpt-3.5-turbo', 'system_prompt': 'you are a helpful ai', 'user_prompt': '', 'temperature': Decimal('0'), 'max_token_response': 5000, 'is_active': True}
                chat_bot_config = cache.get(agent_id)
                print('chat_bot_config in redis',chat_bot_config,type(chat_bot_config))
                if not chat_bot_config:
                    chat_bot_config_obj = BOT_LLM_CONFIG.objects.get(agent_id=agent_id)
                    chat_bot_config = model_to_dict(chat_bot_config_obj)
                    print('chat_bot_config in SQL',chat_bot_config,type(chat_bot_config))
            
                

                """使用celery 来处理异步任务,回复消息
                """
                # 先判断一下用哪个模型回复
                if 'gpt' in chat_bot_config['llm_model_name']:
                    print("使用gpt模型来回复")
                
                    async_send_messages_through_gpt.delay(message_type=msg_type,
                                                        received_message=message_content,
                                                        from_user_name=from_user_name,
                                                        agent_id=agent_id,
                                                        chat_bot_config=chat_bot_config,
                                                        event=event
                                                        )    
                
                
                if 'claude' in chat_bot_config['llm_model_name']:
                    print("使用claude模型来做回复")
                
            
                return HttpResponse('ok', content_type="application/xml")
            
            # 如果发送的是图片,就把图片保存到minio 中，然后数据库也存储一份
            elif msg_type == 'image':
                print('接受到了图片信息')
                
                """保存image到minio中,根据不同的用户来保存到地址images/用户名/图片名
                """
                # 这里的 tousername 是 corpid,from username 才是发信人
                to_user_name = decrypted_message_xml.find('ToUserName').text
                from_user_name = decrypted_message_xml.find('FromUserName').text
                agent_id = decrypted_message_xml.find('AgentID').text
                create_time = decrypted_message_xml.find('CreateTime').text
                msg_type = decrypted_message_xml.find('MsgType').text
                msg_id = decrypted_message_xml.find('MsgId').text
                image_url = decrypted_message_xml.find('PicUrl').text
                media_id = decrypted_message_xml.find('MediaId').text
                # print('to_user_name',to_user_name)
                # print('agent_id',agent_id)
                # print('from_user_name',from_user_name)
                
                # create_time 是 2024-03-26 03:13:30 字符串
                # print('create_time',timestamp_to_datetime_str(int(create_time)))
                # print('msg_type',msg_type)
                # print('msg_id',msg_id)
                # print('image_url',image_url)
                print('media_id',media_id)
                
                # 保存图片, celery 来完成
                async_save_image_to_minio.delay(
                                                from_user_name=from_user_name,
                                                agent_id=agent_id,
                                                create_time=create_time,
                                                media_id=media_id,
                                                )
                
                return HttpResponse('ok', content_type="application/xml")
            
            # 如果发送的语音
            elif msg_type == 'voice':
                print('接受到了音频信息')
                # 这里的 tousername 是 corpid,from username 才是发信人
                to_user_name = decrypted_message_xml.find('ToUserName').text
                from_user_name = decrypted_message_xml.find('FromUserName').text
                agent_id = decrypted_message_xml.find('AgentID').text
                create_time = decrypted_message_xml.find('CreateTime').text
                msg_type = decrypted_message_xml.find('MsgType').text
                msg_id = decrypted_message_xml.find('MsgId').text
                media_id = decrypted_message_xml.find('MediaId').text
                # print('to_user_name',to_user_name)
                # print('agent_id',agent_id)
                # print('from_user_name',from_user_name)
                
                # create_time 是 2024-03-26 03:13:30 字符串
                # print('create_time',timestamp_to_datetime_str(int(create_time)))
                # print('msg_type',msg_type)
                # print('msg_id',msg_id)
                # print('image_url',image_url)
                print('voice的media_id',media_id)
                
                # 保存视频到 minio, celery 来完成
                async_save_voice_to_minio.delay(
                                                from_user_name=from_user_name,
                                                agent_id=agent_id,
                                                create_time=create_time,
                                                media_id=media_id,
                                               )
                return HttpResponse('ok', content_type="application/xml")
            
            # 如果发送的视频
            elif msg_type == 'video':
                print('接受到了视频信息') 
                # 这里的 tousername 是 corpid,from username 才是发信人
                to_user_name = decrypted_message_xml.find('ToUserName').text
                from_user_name = decrypted_message_xml.find('FromUserName').text
                agent_id = decrypted_message_xml.find('AgentID').text
                create_time = decrypted_message_xml.find('CreateTime').text
                msg_type = decrypted_message_xml.find('MsgType').text
                msg_id = decrypted_message_xml.find('MsgId').text
                media_id = decrypted_message_xml.find('MediaId').text
                # print('to_user_name',to_user_name)
                # print('agent_id',agent_id)
                # print('from_user_name',from_user_name)
                
                # create_time 是 2024-03-26 03:13:30 字符串
                # print('create_time',timestamp_to_datetime_str(int(create_time)))
                # print('msg_type',msg_type)
                # print('msg_id',msg_id)
                # print('image_url',image_url)
                print('视频media_id',media_id)
                
                # 保存视频到 minio, celery 来完成
                async_save_video_to_minio.delay(
                                                from_user_name=from_user_name,
                                                agent_id=agent_id,
                                                create_time=create_time,
                                                media_id=media_id)
                
                
                return HttpResponse('ok', content_type="application/xml")
                
               
            
            
            else:
                print("其他情况,可能是定位,其他")
                to_user_name = decrypted_message_xml.find('ToUserName').text
                from_user_name = decrypted_message_xml.find('FromUserName').text
                # 其他状况
                response_content = '''我现在还读不懂你的消息'''
                
                # 构造响应消息并加密
                response_xml = f"""
                <xml>
                    <ToUserName><![CDATA[{to_user_name}]]></ToUserName>
                    <FromUserName><![CDATA[{from_user_name}]]></FromUserName>
                    <CreateTime>{int(time.time())}</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[{response_content}]]></Content>
                </xml>
                """
                encrypted_response = encrypt_message(response_xml)

                # 生成新的消息签名
                new_msg_signature = generate_signature(RECEIVE_MESSAGE_TOKEN, timestamp, nonce, encrypted_response)
                
                # 构造被动响应包
                reply_xml = f"""
                <xml>
                <Encrypt><![CDATA[{encrypted_response}]]></Encrypt>
                <MsgSignature><![CDATA[{new_msg_signature}]]></MsgSignature>
                <TimeStamp>{timestamp}</TimeStamp>
                <Nonce><![CDATA[{nonce}]]></Nonce>
                </xml>
                """

                return HttpResponse(reply_xml, content_type="application/xml")
            
            
            
            
                """这里开始是被动回复消息。就是接受消息马上发送,非异步,只写了文字版，没有写图片或者音频
                """
                # # 这里开始是被动回复,非异步任务
                # # 假设响应消息内容为 "Hello, this is a reply."
                # # response_content = '''你好'''
                
                # # start_messages是历史回复消息
                # start_messages = []
                # OpenAIObj = OpenAIModel()
                # # print(OpenAIObj.reply_message('你好',start_messages))
                # GPT_response = OpenAIObj.reply_message(message_content,start_messages,'你会先自我介绍，你的名字叫 qin')
                # print(GPT_response)
                # response_content = GPT_response[0]
                # print(response_content)
                
                
                # # 构造响应消息并加密
                # response_xml = f"""
                # <xml>
                #     <ToUserName><![CDATA[{to_user_name}]]></ToUserName>
                #     <FromUserName><![CDATA[{CORPID}]]></FromUserName>
                #     <CreateTime>{int(time.time())}</CreateTime>
                #     <MsgType><![CDATA[text]]></MsgType>
                #     <Content><![CDATA[{response_content}]]></Content>
                # </xml>
                # """
                # encrypted_response = encrypt_message(response_xml)

                # # 生成新的消息签名
                # new_msg_signature = generate_signature(RECEIVE_MESSAGE_TOKEN, timestamp, nonce, encrypted_response)
                
                # # 构造被动响应包
                # reply_xml = f"""
                # <xml>
                # <Encrypt><![CDATA[{encrypted_response}]]></Encrypt>
                # <MsgSignature><![CDATA[{new_msg_signature}]]></MsgSignature>
                # <TimeStamp>{timestamp}</TimeStamp>
                # <Nonce><![CDATA[{nonce}]]></Nonce>
                # </xml>
                # """

                # return HttpResponse(reply_xml, content_type="application/xml")
            
            
            
            
            