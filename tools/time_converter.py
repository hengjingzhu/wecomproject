from datetime import datetime, timezone, timedelta

def timestamp_to_datetime_str(timestamp, tz_offset_hours=8):
    """
    将给定的时间戳转换为指定时区的年月日时分秒格式字符串。

    参数:
    - timestamp: 时间戳，整数，表示自1970年1月1日以来的秒数。
    - tz_offset_hours: 时区偏移量（小时），默认为8（即上海时区）。

    返回:
    - 指定时区的年月日时分秒格式的字符串。
    """
    # 创建时区对象
    target_tz = timezone(timedelta(hours=tz_offset_hours))
    
    # 将时间戳转换为UTC时间的datetime对象
    utc_time = datetime.utcfromtimestamp(timestamp)
    
    # 转换为目标时区时间
    target_time = utc_time.replace(tzinfo=timezone.utc).astimezone(target_tz)
    
    # 格式化输出
    return target_time.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    # 示例：使用函数将时间戳1710962798转换为上海时区的时间字符串
    print(timestamp_to_datetime_str(1710962798))
