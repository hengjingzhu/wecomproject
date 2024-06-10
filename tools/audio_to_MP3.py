import subprocess
import io

def convert_amr_to_mp3(amr_data):
    # 将 AMR 数据写入 BytesIO 对象
    amr_stream = io.BytesIO(amr_data)
    
    # 调用 ffmpeg 将 AMR 从标准输入转换为 MP3 输出到标准输出
    process = subprocess.Popen(['ffmpeg', '-y', '-i', '-', '-b:a', '192k', '-q:a', '0', '-f', 'mp3', '-'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 从内存中读取 AMR 数据并捕获转换后的 MP3 数据
    mp3_data, _ = process.communicate(input=amr_stream.getvalue())
    
    # 将 MP3 数据再次放入 BytesIO 对象以模拟文件操作
    mp3_stream = io.BytesIO(mp3_data)
    return mp3_stream
    