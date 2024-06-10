import json
from ..agent_tools_choose.describe_picture_by_urls import describe_the_picture_by_urls,generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls
from ..agent_tools_choose.get_media_file_from_DB import get_media_file_from_DB


available_functions = {
    "get_media_file_from_DB":get_media_file_from_DB,
    "describe_the_picture_by_urls":describe_the_picture_by_urls,
    "generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls":generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls,
}


agent_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_media_file_from_DB",
                "description": "This function is triggered only when the user asks about the media query tasks. It retrieves media files (only pictures, videos) from the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_delta_string": {
                            "type": "string",
                             "description": "The time query string needs to be specific if asked about the recent past, e.g., 'last 30 minutes'.\
                            The value shoule be 'no specific time detected' if user enquiry media around recent past or just now or didn't give the specific time range.",
                        },
                        "media_type": {
                            "type": "string",
                            "description": "The type of media required by the user, limited to 'image' or 'video'",
                        },
                        "number_of_files":{
                            "type": "string",
                            "description": "The number of media files requested by the user, e.g., '5'. \
                                            The maximum number is 10. If the user does not specify the number of media files, return 1.",
                        },
                    },
                    "required": ["time_delta_string","media_type","number_of_files"],
                },
            },
        },
        
        
        {
        "type": "function",
        "function": {
            "name": "describe_the_picture_by_urls",
            "description": "This function describes the pictures or videos or generate general copywriting by providing URLs. \
                            It is triggered only when the user has asked for a general description of the media or gengerate general copywriting without specific social medias.\
                            Please recall this function if user didn't specify any social media.",
        "parameters": {
                    "type": "object",
                    "properties": {
                        "media_files_list": {
                            "type": "string",
                            "description": "the list of media files when function 'get_media_file_from_DB' was provided, maintaining the same JSON format as input.",
                        },
                    },
                    "required": ["media_files_list",],
                },
        },
        },
        
        {
        "type": "function",
        "function": {
            "name": "generate_Xiaohongshu_copywriting_the_pictures_or_video_by_urls",
            "description": "This function generates coptwriting for only Xiaohongshu(Little Red Book) by providing pictures or video through URLs. \
                            It is only triggered when the user has asked for generating the Xiaohongshu(Little Red Book) coptwriting.\
                            Please don't recall this funcion if user didn't specify any social media",
        "parameters": {
                    "type": "object",
                    "properties": {
                        "media_files_list": {
                            "type": "string",
                            "description": "the list of media files when function 'get_media_file_from_DB' was provided, maintaining the same JSON format as input.\
                                            the json input format must like: [{\"media_type\":\"image\",\"image_url\":\"the image url address\"},...]",
                        },
                    },
                    "required": ["media_files_list",],
                    
                },
        },
        },
        
    ]
