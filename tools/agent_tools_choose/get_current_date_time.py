from datetime import datetime
def get_current_date_time_weekday():
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期和时间的显示
    formatted_date = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%H:%M:%S")
    # 获取周几
    weekday_number = now.weekday()

    # 将数字转换为周几的名称
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_name = days_of_week[weekday_number]
    
    
    return {"currentDate":formatted_date,"currentTime":formatted_time,"currentWeekday":weekday_name}


if __name__ == '__main__':
    print(get_current_date_time_weekday())