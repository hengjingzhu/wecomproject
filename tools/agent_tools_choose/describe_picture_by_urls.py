from ..wecom_tools import WECOMM
from ..claude_tools.description_images import DESCRIPTION_IMAGE_THROUGH_CLAUDE
import json



# 这里是描述照片的业务逻辑,使用 claude 来描述
def describe_the_picture_by_urls(media_files_list,user,user_query,agent_id,GPT_reply_content):
    
    
    print('media_files_list in describe_the_picture_by_urls',media_files_list)
    print(json.loads(media_files_list))
    
    if media_files_list:
    
        data={
                    "touser" : user,
                    "msgtype" : 'text',
                    "agentid" : agent_id,
                    "text" : {
                        "content" : "努力分析中.....💦💦💦💦💦"
                    },
        }
        WECOMM(agentId=agent_id).send_message(data=data)

        image_analysis_prompt = f"""
                                    You have perfect vision and pay great attention to detail which makes you an expert at analysing images, and your assignment includes the following tasks:\
                                    Before providing the answers in a <answer> tag, think step by step in <thinking> tags and analyze every part of the images.\
                                    1. Extract all the detailed information from all the images, including any text and data present.\
                                    2. Carefully verify that the extracted information accurately matches the content depicted in these images.\
                                    3. Describe every data point in Chinese you see in the image.\
                                    4. Given the user_query: {user_query}. Please decompose this user_query into smaller, more detailed questions.\
                                    5. Answer all above specific questions in more than 1000 words in Chinese. \
                                    6. All the answers shoule be in one <answer> tag.
                                """
    

        result = DESCRIPTION_IMAGE_THROUGH_CLAUDE(image_analysis_prompt=image_analysis_prompt,
                                                  user_query=user_query,
                                                  image_list=json.loads(media_files_list),
                                                  temperature=0
                                                  ).run()
    
        print(result)
    # print('user,user_query,agent_id in describe_the_picture_by_urls',user,user_query,agent_id)
    return result


def generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls(media_files_list,user,user_query,agent_id,GPT_reply_content):
    print('media_files_list in generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls',media_files_list)
    print(json.loads(media_files_list))
    
    if media_files_list:
    
    
        data={
                    "touser" : user,
                    "msgtype" : 'text',
                    "agentid" : agent_id,
                    "text" : {
                        "content" : "小红书文案生成中.....❤️"
                    },
        }
        WECOMM(agentId=agent_id).send_message(data=data)
        
        
        Xiaohongshu_copywriting_prompt = f"""
                                You are now a top-tier content creation assistant for KOLs (Key Opinion Leaders). Your task is to write a Xiaohongshu (Little Red Book) post as a Chinese influencer, based on the image content and the user's query. The post should meet the following requirements:
                                1. Start with a captivating introduction.
                                2. Provide at least three paragraphs related to the theme, highlighting their unique features and appeal. Use emojis in your paragraphs to make them more engaging and fun.
                                3. For each paragraph, include at least one emoji that matches the described content. These emojis should be visually appealing and help make your description more vivid.
                                4. Focus on the relevant content based on the user's query.
                                5. Style considerations:
                                    - KOL style: sincere, humorous, and down-to-earth.
                                    - Based on your understanding of the "country and region" of the user, decide whether to use emojis or kaomojis.
                                    - Include multiple emojis in each paragraph, placed at different positions.
                                    - The style should be lively, eye-catching, and conversational. Avoid formal language.
                                6. End with at least five keywords, each starting with the symbol #.
                                7. The post should be at least 100 words long.
            
                                    please think step by step. 
                                    现在用户的query是:'{user_query}'
                                """
        result = DESCRIPTION_IMAGE_THROUGH_CLAUDE(image_analysis_prompt=Xiaohongshu_copywriting_prompt,
                                                  user_query=user_query,
                                                  image_list=json.loads(media_files_list),
                                                  temperature=0.2
                                                  ).run()
    
        print(result)
        return result