from .get_current_date_time import get_current_date_time_weekday
from ..config import *
from ..wecom_tools import WECOMM 
from openai import OpenAI
import json
from apimessage.models import MyStaticModel

from datetime import datetime,timedelta

def convert_to_chinese_readable(date_string):
    # 将字符串解析为 datetime 对象
    date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
    
    # 定义中文月份
    chinese_months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    
    # 将日期时间对象转换为中文可读模式
    chinese_readable_date = f"{date_object.year}年{chinese_months[date_object.month - 1]}{date_object.day}日 {date_object.hour}时{date_object.minute}分{date_object.second}秒"
    
    return chinese_readable_date


client = OpenAI(api_key=SECRETKEY)


def get_media_file_from_DB(time_delta_string,media_type,number_of_files,user,user_query,agent_id,GPT_reply_content):
    
    model_name = "gpt-3.5-turbo"
    
    current_date_time_weekday = get_current_date_time_weekday()
    currentDate = current_date_time_weekday['currentDate']
    currentTime = current_date_time_weekday['currentTime']
    currentWeekday = current_date_time_weekday['currentWeekday'] 
    
    print('time_delta_string',time_delta_string,currentDate,currentTime)
    # 这个是不指定具体日期，从后往前查询
    if GPT_reply_content:
        data={
                    "touser" : user,
                    "msgtype" : 'text',
                    "agentid" : agent_id,
                    "text" : {
                        "content" : GPT_reply_content
                    },
        }
        WECOMM(agentId=agent_id).send_message(data=data)
    
    
    # 如果是没指定时间段逻辑，查找的是45分钟之前的图片信息
    if time_delta_string == 'no specific time detected':
        
        # 获取当前时间
        current_time = datetime.now()

        # 计算60分钟前的时间
        thirty_minutes_ago = current_time - timedelta(minutes=45)
        
        
        example = '''Q: 第二张图片
                    A: {"exec_code":"MyStaticModel.objects.filter(username=user,agent_id=agent_id,created_time__gte=thirty_minutes_ago).exclude(image='').order_by('created_time')[:1]","response_content:"GPT response"}

                    Q: 倒数第二张图片
                    A: {"exec_code":"MyStaticModel.objects.filter(username=user,agent_id=agent_id,created_time__gte=thirty_minutes_ago).exclude(image='').order_by('-created_time')[:1]","response_content:"GPT response"}

                    Q: 这二张图片
                    A: {"exec_code":"MyStaticModel.objects.filter(username=user,agent_id=agent_id,created_time__gte=thirty_minutes_ago).exclude(image='').order_by('-created_time')[:2]","response_content:"GPT response"}

                    Q: 刚刚上传的两张图片
                    A: {"exec_code":"MyStaticModel.objects.filter(username=user,agent_id=agent_id,created_time__gte=thirty_minutes_ago).exclude(image='').order_by('-created_time')[:2]","response_content:"GPT response"}
                   '''
        userPrompt = f'''
                        Task 1:
                        Generate a Python Django 3.2 code snippet to query a Static Model's queryset based on user input. For example: MyStaticModel.objects.filter(username=user, agent_id=agent_id, created_time__gte=thirty_minutes_ago).exclude(image='').order_by('-created_time')

                        Here's the query specification:

                        """
                        The name of the model is <MyStaticModel>.
                        Fields to query are <username>, <agent_id>, <created_time>.

                        The value of username is always the variable user and cannot be changed.
                        The value of agent_id is always the variable agent_id and cannot be changed.
                        created_time is always greater than thirty_minutes_ago.
                        After querying, results are to be sorted based on the field <created_time>, with -created_time indicating sorting from newest to oldest.
                        """

                        You need to sort based on the user's semantics first, then slice the resulting queryset into smaller ones. The final result must also be a queryset, even if the user asks for a specific image.

                        Task 2:
                        Respond to the user in Simplified Chinese, replace the content "GPT response" in your own createive words. such as: acknowledging understanding of their request,I'll handle your task from here. Do not return any code. Keep the tone friendly and sincere.

                        Here are examples:{example}:
                        
                        The final output must be in JSON format with the following keys: exec_code, response_content. Return only the JSON output as the final output, without any additional content.
                       
                        Now, this is the user query: {user_query}
                        '''
        messages = [{"role": "user", "content": userPrompt}]
        response = client.chat.completions.create(
            model = model_name,
            messages = messages,
            temperature=0,
            response_format={ "type": "json_object" },
        )
        print('response.choices[0].message.content',response.choices[0].message.content)
        
        
        try:
            search_image_query = eval(json.loads(response.choices[0].message.content)['exec_code'])
            gpt_response = json.loads(response.choices[0].message.content)['response_content']
            data={
                    "touser" : user,
                    "msgtype" : 'text',
                    "agentid" : agent_id,
                    "text" : {
                        "content" : gpt_response
                        },
            }
            WECOMM(agentId=agent_id).send_message(data=data)

        
        except Exception as e:
            return f"不好意思检索媒体失败,请重新询问+{e} "
        
        print('search_image_query111111',search_image_query)



        
    
    # 这个是指定具体日拉取图片，需要计算具体日期
    else:
        example = '{"startDateTime": "2024-05-08T04:00:00","endDateTime": "2024-05-08T05:00:00"}'
        userPrompt = f'''you task is calculating the past time range that user asked,please note never calcuate the future time.
                        The current date is {currentDate},current time is {currentTime},current weekday is {currentWeekday}.
                        The final output should be in json format with following keys: startDateTime,endDateTime and the value format must be '%Y-%m-%dT%H:%M:%S'.
                        for example: {example}
                        Now,The User is asked : {time_delta_string}
                        '''
        
        messages = [{"role": "user", "content": userPrompt}]
        response = client.chat.completions.create(
            model = model_name,
            messages = messages,
            temperature = 0,
            response_format={ "type": "json_object" },
        )
        
        """ {
            "startDateTime": "2024-05-01T00:00:00",
            "endDateTime": "2024-05-01T12:00:00"
            }
        """
        
        time_range = json.loads(response.choices[0].message.content)
        # print('user query startDateTime and endDateTime',response.choices[0].message.content)
        
        startDateTime = convert_to_chinese_readable(time_range['startDateTime'])
        endDateTime = convert_to_chinese_readable(time_range['endDateTime'])
        
        # send the message to user
        time_range_in_chinese = f'🤔🤔🤔\n\n正在回忆\n\n从\n{startDateTime}\n到\n{endDateTime} \n\n最新的 {number_of_files} 张图片。'
        
        data={
                    "touser" : user,
                    "msgtype" : 'text',
                    "agentid" : agent_id,
                    "text" : {
                        "content" : time_range_in_chinese
                    },
        }
        WECOMM(agentId=agent_id).send_message(data=data)
            
        """retrieve the media file through minio
        return:[{"media_type":"image_url:"https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1713294652.jpeg"},...]
        """
        # 先把时间字符串编程 datetime 格式
        start_datetime = datetime.fromisoformat(time_range['startDateTime'])
        end_datetime = datetime.fromisoformat(time_range['endDateTime'])
        
        
        
        # 根据时间用户名,和哪个用户对话的来搜索图片,根据时间倒叙排序，然后取值。
        
        search_image_query = MyStaticModel.objects.filter(created_time__gte=start_datetime, created_time__lte=end_datetime,
                                                        username=user,
                                                        agent_id=agent_id
                                                        ).exclude(image='').order_by('-created_time')[:int(number_of_files)]
        
    print('final_result',search_image_query)
    
    # 如果final_result 有值就返回
    final_result = []
    if search_image_query:
        print('search_image_query',search_image_query)
        for obj in search_image_query:
            
            final_result.append(
                {'media_type':f'{media_type}','image_url':obj.image.url.split('?')[0]}
                )
        
        data={
                "touser" : user,
                "msgtype" : 'text',
                "agentid" : agent_id,
                "text" : {
                    "content" : f"我会根据找到的 {len(final_result)} 张图片来完成以下任务👏👏👏"
                },
        }
        WECOMM(agentId=agent_id).send_message(data=data)
        
        
        final_result = json.dumps(final_result)
        print(final_result)
        # final_result = json.dumps([
        #     {'media_type':f'{media_type}','image_url':'https://media.unexus.cn:9000/wecom/images/ZhuHengJing/ZhuHengJing_1713383264.jpeg'},
        #     {'media_type':f'{media_type}','image_url':'https://media.unexus.cn:9000//wecom/images/ZhuHengJing/ZhuHengJing_1713294652.jpeg'}])

        return f"These are the all image files that user required: {final_result}"
    else:
        return f"you have no image files uploaded during this time range"

if __name__ == '__main__':
    pass