import base64
import httpx
from PIL import Image
from io import BytesIO
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import anthropic
from tools.config import *
import re
import json

user_query = '请详细描述'


model_name = 'claude-3-haiku-20240307'
max_tokens = '4096'
temperature = 0

class DESCRIPTION_IMAGE_THROUGH_CLAUDE():
    
    # image_list = [{'media_type':'image','image_url':'https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1713383264.jpeg'},...]
    def __init__(self,image_list,image_analysis_prompt,user_query=user_query,model_name = model_name,max_token=max_tokens,temperature = temperature) -> None:
        self.model_name = model_name
        self.max_token = max_token
        self.temperature = temperature

        self.image_list = image_list
        self.user_query = user_query
        
        self.image_analysis_prompt = image_analysis_prompt

        
    """fetch online image
    """
    # 最多重试8次 # 指数退避策略，初始等待1秒，最大等待10秒 # 仅在请求错误时重试
    @retry(stop=stop_after_attempt(8), wait=wait_exponential(multiplier=1, max=10),retry=retry_if_exception_type(httpx.RequestError))
    def fetch_image(self,image_url):
        response = httpx.get(image_url, timeout=10.0)  # 设置超时时间为10秒
        response.raise_for_status()  # 如果响应状态码不是200系列，将抛出异常
        return response.content

    """ convert imagedata to base64 data
        input:  [{'media_type':'image','image_url':'https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1713383264.jpeg'},...]
        output: [{'media_type;:'image/jpeg','image_data':'xxxxx',..........}]
    """
    def convert_imageUrl_base64(self,image_list):
        result = []
        for image_info in image_list:
            image_url = image_info['image_url']
            
            try:
                image_content = self.fetch_image(image_url)
                image = Image.open(BytesIO(image_content))
                if image.format == 'JPEG' or image.format == 'JPG':
                    image_media_type = 'image/jpeg'
                elif image.format == 'PNG':
                    image_media_type = 'image/png'
                elif image.format == 'GIF':
                    image_media_type = 'image/gif'
                else:
                    image_media_type = 'image/jpeg'
                #print(image.format,type(image.format))
                #print('image_content',type(image_content),image_content[0:100])
                image_data = base64.b64encode(image_content).decode('utf-8')
                #print('image_data',image_data)
                result.append({'media_type': image_media_type, 'image_data': image_data})
                #print(result)
            except httpx.HTTPStatusError as e:
                print(f"HTTP Status Error fetching {image_url}: {e}")
            except Exception as e:
                print(f"An error occurred while fetching or encoding {image_url}: {e}")

        return result

    def input_messages_claude_image(self,image_list_base64):
        # image_list_base64 = image_list_base64
        input_messages = [
            {'role':"user",
            "content":[]
            }
        ]
        for i in image_list_base64:
            if 'image' in i['media_type']:
                input_messages[0]["content"].append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": i['media_type'],
                            "data": i['image_data'],
                        },
                    },
                )

        input_messages[0]["content"].append({
            'type':'text',
            'text':self.image_analysis_prompt
        })
        
        return input_messages


    def description_image_claude(self,input_messages):
        message = anthropic.Anthropic(api_key=ANTHROPIC_SECRETKEY).messages.create(
            model=model_name,
            max_tokens=4096,
            temperature=self.temperature,
            messages=input_messages
        )
        return message.content[0].text


    def run(self):
        
        image_list_base64 = self.convert_imageUrl_base64(self.image_list)
        input_messages = self.input_messages_claude_image(image_list_base64)
        #print(input_messages)
        result = self.description_image_claude(input_messages)
        
        # exact the final answer from the result
        # 使用正则表达式提取<answer>标签内的内容
        match = re.search(r'<answer>(.*?)</answer>', result, re.DOTALL)
        if match:
            answer_json = match.group(1).strip()
            print('answer_json',answer_json)
            # 解析为JSON
            # answer_data = json.loads(answer_json)
            # print(answer_data)
            # 提取 'final_answer' 字段
            # print(answer_data)
            final_answer = answer_json
        else:
            # 如果没有提取出来就返回全部答案包括思考过程
           final_answer = result
        return final_answer
    
    
    
    

if __name__ == '__main__':
    # from tools.claude_tools.description_images import DESCRIPTION_IMAGE_THROUGH_CLAUDE
    # image_list = [{'media_type':'image','image_url':'https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1714203454.jpeg'},
    #               {'media_type':'image','image_url':'https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1714203526.jpeg'}]
    
    # DESCRIPTION_IMAGE_THROUGH_CLAUDE(image_list=image_list).run()
    pass