import base64
import httpx


# 把在线的图片转为 base64数据
def ImgURL_to_Base64(image_url):

    image_url = image_url
    image_media_type = "image/jpeg"
    image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
    return image_data


if __name__ == '__main__':
    print(ImgURL_to_Base64('https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg'))