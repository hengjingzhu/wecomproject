
# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wecom.settings')
# django.setup()
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from tools.config import *
import time
import traceback
import requests
import redis
import inspect
from io import BytesIO
from PIL import Image
import json
from urllib.parse import urlparse


corpid = CORPID
# corpsectet = CORPSECRET

redis_host = REDIS_EXTERNAL_HOST
redis_port = REDIS_PORT
redis_database = REDIS_DATABASE
redis_password = REDIS_PASSWORD

access_token_expiry_time = 7000
max_retry_time = 5





class WECOMM():
    
    
    def __init__(self,agentId) -> None:
        self.agentID = agentId    
        self.access_token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={json.loads(WECOM_CHAT_BOT_CORPSECRET)[agentId]}'
        self.redis_connection = redis.Redis(host=redis_host,
                                            port=redis_port,
                                            db=redis_database,
                                            password=redis_password,
                                            decode_responses=True
                                            )
        self.retry_time = 0
    
    def Get_access_token(self):
        """get a wecomm access token

        Returns:
            str: wecomm access token.eg:vD4bqeNVz9GqN9MTOTYMiy-vwRB9vTCZkTrFhEHSimUTZgz_Fy9PqXAAQ3PMk_kNVcat656A5WARJp65qsHu_4CBJfaAIq3imViEpg7PSJLqsy3-qgFTHzVQWSoYE-hWqPdscwmEKv8hcPzn80WumCQ3ecSFLMKuHz__y1feBkVgf09JbrMnbetrGQ_0JENWxV5ErMUpT_0vGKpaB-dx9A
        """
        access_token_key = self.agentID+'_access_token'
        try:
            # get a exist access token from redis
            access_token = self.redis_connection.get(access_token_key)
            print('access_token in redis',access_token)
            
            # if access token is not in the redis,get a new one
            if not access_token:
                response = requests.get(self.access_token_url)
                if response.status_code == 200:
                    access_token = response.json()["access_token"]
                    # save access token to redis
                    self.redis_connection.setex(access_token_key,access_token_expiry_time,access_token)
            
            # clear the retry time
            self.retry_time = 0
            return access_token
        
        except Exception as e:

            if self.retry_time <= max_retry_time:
                time.sleep(3)
                self.retry_time +=1
                print(f"this is {self.retry_time} times retry to get token")
                return self.Get_access_token()
            #traceback.format_exc()来打印具体错误信息
            error_message = traceback.format_exc()
            print('Get_access_token error',
                  'error message',error_message,
                  'error class name',self.__class__.__name__,
                  'error function name',inspect.currentframe().f_code.co_name)
                    
    def resize_image(self,image_bytes, max_size_mb=4,target_quality=95,max_short_side=768, max_long_side=2000):
        """如果图片大于等于5mb的话会被压缩,或者要满足gpt4o对图片的要求image should be less than 768px and the long side should be less than 2,000px

        Args:
            image_bytes (_type_): _description_
            max_size_mb (int, optional): _description_. Defaults to 5.
            target_quality (int, optional): _description_. Defaults to 95.

        Returns:
            _type_: _description_
        """
        # Open image from bytes
        image = Image.open(BytesIO(image_bytes))
        
        # 检查并打印初始图像信息
        # print(f"Original format: {image.format}, mode: {image.mode}, size: {len(image_bytes) / (1024 * 1024)} MB")
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        
        # gpt-4o url requirements: the short side of the image should be less than 768px and the long side should be less than 2,000px
        # 缩小图像分辨率,
        # 获取当前图像尺寸
        width, height = image.size
        if width > height:
            long_side = width
            short_side = height
        else:
            long_side = height
            short_side = width
        # 判断是否需要缩小分辨率
        if long_side > max_long_side or short_side > max_short_side:
            if long_side / max_long_side > short_side / max_short_side:
                scale_factor = max_long_side / long_side
            else:
                scale_factor = max_short_side / short_side

            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
                
            image = image.resize((new_width, new_height), Image.LANCZOS)

    
        output = BytesIO()
        image.save(output, format='JPEG', quality=target_quality)
        resized_image_bytes = output.getvalue()
        
        
        # 压缩图像质量以满足最大文件大小要求，满足claude的要求
        if len(image_bytes) / (1024 * 1024) >= max_size_mb:
           
            while True:
                # Reset output buffer
                output.seek(0)
                output.truncate()
                
                # Save image to bytes with specified quality
                image.save(output, format='JPEG', quality=target_quality,exif=image.info.get('exif'))
                # Check size
                if output.tell() / (1024 * 1024) <= max_size_mb:
                    break
                # Reduce quality for next iteration
                target_quality -= 5
                

            resized_image_bytes = output.getvalue()
            # Check the final image size and format
            # resized_image = Image.open(BytesIO(resized_image_bytes))
            # print(f"Resized format: {resized_image.format}, mode: {resized_image.mode}")
            # print(f"Resized size: {len(resized_image_bytes) / (1024 * 1024)} MB")
            return resized_image_bytes
        else:
            # If image size is already below 5MB, return original image data
            return image_bytes
      
    def Get_media_data(self,media_id):
        access_token = self.Get_access_token()
        Get_media_data_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}'
        response = requests.get(url=Get_media_data_url)
        response.raise_for_status()  # 确保请求成功
        if response.status_code == 200:
            print('media请求结果成功')
            
            original_image_bytes = response.content
            resized_image_bytes = self.resize_image(original_image_bytes)
            return resized_image_bytes
        
    def Get_voice_data(self,media_id):
        access_token = self.Get_access_token()
        Get_media_data_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}'
        response = requests.get(url=Get_media_data_url)
        response.raise_for_status()  # 确保请求成功
        if response.status_code == 200:
            print('media请求结果成功,voice data')
            return response.content
    
    # 上传临时素材给到wecomm,得到一个 media ID,type 分别有图片（image）、语音（voice）、视频（video），普通文件（file)
    # 最多重试5次 # 指数退避策略，初始等待1秒，最大等待10秒 # 仅在请求错误时重试
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10))
    def Upload_media_file(self,media_url,type='image'):
        access_token = self.Get_access_token()
        Upload_media_file_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={type}'

        media_response = requests.get(media_url)
        if media_response.status_code == 200:
            img_data = BytesIO(media_response.content)
        filename = os.path.basename(urlparse(media_url).path)
        files = {
            "media": (filename, img_data, "application/octet-stream")
        }
        response = requests.post(Upload_media_file_url, files=files)
    
        if response.status_code == 200:
            result = response.json()
            try: 
                media_id = result['media_id']
                return media_id
            except Exception as e:
                return f'upload media faile +{e}'
                
    # 发信信息给到指定用户    
    def send_message(self,data={
                        "touser" : 'zhuhengjing',
                        "msgtype" : "text",
                        "agentid" : 1000002,
                        "text" : {
                            "content" : '这是测试回复'
                        },
                    }):
        
        access_token = self.Get_access_token()
        send_message_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        
        data = data

        response = requests.post(send_message_url,json=data)
        # print(response.text)
        # 这是返回结果{"errcode":0,"errmsg":"ok","msgid":"mrVtVXE39it1tWVvd57npAlvYPK1_QbWrsoP5nAJpNWL9AekCJrk7qTXgahSlAq4J-h_4p794TcEXlqoQmO8kA"}
        return response.text

if __name__ =='__main__':
    # from tools.wecom_tools import WECOMM
    # result = WECOMM().send_message()
    # print(result,type(result))
    # WECOMM(agentId=100002).Get_media_data(media_id='1bzUHZd-nlQ086gWEtUHoHA6KJPdQ6RQjPXkyMv-frTqb9z0mRxSEGdWzgoiWAXqV')
    WECOMM(agentId='1000002').Upload_media_file(media_url='http://106.14.9.212:9100/wecom/images/ZhuHengJing/ZhuHengJing_1713294652.jpeg',type='image')
    WECOMM(agentId='1000002').send_message(data={
                        "touser" : 'zhuhengjing',
                        "msgtype" : "image",
                        "agentid" : 1000002,
                        "image" : {
                                "media_id" : "30i4vSu-cUtd_pV3_ROmjKUblbxkMktxB9igyWri0-exkFpu9DFVLVa4WnpnxDkjo"
                        },
                    })