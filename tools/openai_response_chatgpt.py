# -*- coding: utf-8 -*-
from .config import *

from openai import OpenAI
import json

from .agent_tools_choose.tools_description import agent_tools,available_functions

client = OpenAI(organization=ORG_ID,
                  api_key=SECRETKEY)


class OpenAIModel():
  
  
  def __init__(self,
               user,
               user_query,
               agent_id,
               max_token_response=MAX_TOKEN_RESPONSE,
               model_temperature=MODEL_TEMPERATURE,
               open_ai_model_name = OPEN_AI_MODEL_NAME
               ) -> None:
    
    self.start_sequence = "assistant"
    self.prompt = "user"
    
    self.OPEN_AI_MODEL_NAME = open_ai_model_name
    self.MAX_TOKEN_RESPONSE = max_token_response
    self.MODEL_TEMPERATURE = model_temperature
    self.user = user
    self.user_query = user_query
    self.agent_id =agent_id
    
  
  def stt_whisper(self,audio_file):
    transcript = client.audio.transcriptions.create(
      file=audio_file,
      model=self.OPEN_AI_MODEL_NAME,
      response_format="text"
    )
    # print(transcript.text)
    return transcript

  


  def get_response(self,messages,system_role_description):
    self.system_message = {"role":"system","content":"you are a helpful ai"}
    # 如果 messages 里的信息第一条角色不是 system 的话，就安排 system 角色
    # print(username)
    
    if messages[0]["role"] != "system":
     

    # 随机返回一个 role, 
    #  random_role_name = random.choices(list(SYSTEM_MESSAGE.keys()))[0]
    #  self.system_message['content'] = SYSTEM_MESSAGE[random_role_name]
      # 把角色描述放到对话第一条信息中
      self.system_message['content'] = system_role_description

      messages.insert(0,self.system_message)

    

    # print('我在get-response',messages)
    response = client.chat.completions.create(
      model=self.OPEN_AI_MODEL_NAME,
      messages=messages,
      temperature=self.MODEL_TEMPERATURE,
      max_tokens=self.MAX_TOKEN_RESPONSE,
      tools=agent_tools,
      tool_choice='auto'
    )

    return response



  def GPT_TOOL_USE(self,messages,GPT_response):
    # print(GPT_response.choices[0].message.tool_calls)
    tool_calls = GPT_response.choices[0].message.tool_calls
    
   
    GPT_reply_content = GPT_response.choices[0].message.content
    print('GPT_response111111111',GPT_response)
    
    
    for tool_call in tool_calls:
        # print(tool_call)
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_args['user'] = self.user
        function_args['agent_id'] = self.agent_id
        function_args['user_query'] = self.user_query
        function_args['GPT_reply_content'] = GPT_reply_content
        
        # print(function_args,type(function_args))
        
        function_response = function_to_call(**function_args)
        # print('we are now using tool:',function_name,'with arguments',function_args)
        # print('function_response',function_response)
        messages.append(GPT_response.choices[0].message)
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        # print(input_messages)
        second_response = client.chat.completions.create(
            model=self.OPEN_AI_MODEL_NAME,
            messages=messages,
            tools=agent_tools,
            tool_choice='auto',
        )

        # print('second_response',second_response)
        # 如果不调用工具了，那就直接返回回复
        if second_response.choices[0].finish_reason == 'stop':
            # print('messages',messages)
            # print('second_response',second_response)
            return second_response
        # 如果接着调用工具，那就递归调用本次
        elif second_response.choices[0].message.tool_calls:
            # print('second response with tool use:',second_response)
            return self.GPT_TOOL_USE(messages,second_response)
  

  def reply_message(self,inputmessage,start_messages,system_role_description='you are an helpful ai'):
    # 调用这个方法的时候，要传入参数 system_role_description

    inputmessage_dict = {"role":self.prompt,"content":inputmessage}
    start_messages.append(inputmessage_dict)
    # print(start_messages)
    # 把组装好的 message 放入到 get_response 的方法中去，得到信息回复
    reply_message_content = self.get_response(messages=start_messages,system_role_description=system_role_description)
  
    # 如果有 tool_calls 走如下
    tool_calls = reply_message_content.choices[0].message.tool_calls
    if tool_calls:
        messages = [
          {"role":"system","content":"you are using tools to answer user query, when you get the answer from function calling tools. just copy full answer to user,please keep same format as answer,do not miss any single word."},
          {"role": "user", "content": inputmessage}
        ]
        reply_message_content = self.GPT_TOOL_USE(messages=messages,GPT_response=reply_message_content)
  
    total_tokens_used = reply_message_content.usage.total_tokens
    reply_message_content = reply_message_content.choices[0].message
    start_messages.append(dict(reply_message_content))
    new_messages = start_messages

    return reply_message_content.content,new_messages,total_tokens_used,reply_message_content

if __name__ == '__main__':

  #from chatgptapiv1.tools.chatgpt.openai_response_chatgpt import OpenAIModel
  start_messages = []


  OpenAIObj = OpenAIModel()
  # print(OpenAIObj.reply_message('你好',start_messages))
  response = OpenAIObj.reply_message('你好啊',start_messages,'你会先自我介绍，你的名字叫 qin')
  print(response)
  # response2 = OpenAIObj.reply_message('你是谁',response[1],'你会先自我介绍，你的名字叫 我是答辩')
  # print(response2)
  # response3 = OpenAIObj.reply_message('你要不帮我想想',response2[1])
  # print(response3)
  # response4 = OpenAIObj.reply_message('你帮我推荐一个游戏',response3[1])
  # print(response4)



