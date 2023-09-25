import hashlib
import datetime


def format_path(path):
    try:
        return path[:-1] if path.endswith('/') else path
    except:
        return path


def md5_string(in_str):
    md5 = hashlib.md5()
    md5.update(in_str.encode("utf8"))
    result = md5.hexdigest()
    return result


def format_pub_time(time_str):
    try:
        if time_str:
            if '秒' in time_str:
                seconds = int(time_str.replace('秒', ''))
                return (datetime.datetime.now() - datetime.timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S')
            elif '分钟' in time_str:
                minutes = int(time_str.replace('分钟', ''))
                return (datetime.datetime.now() - datetime.timedelta(minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')
            elif '小时' in time_str:
                hours = int(time_str.replace('小时', ''))
                return (datetime.datetime.now() - datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
            elif '天' in time_str:
                days = int(time_str.replace('天', ''))
                return (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                if '年' in time_str:
                    return time_str.replace('日', '日 ').replace('年', '-').replace('月', '-').replace('日', '-') + ':00'
                else:
                    current_year = str(datetime.date.today().year)
                    return current_year + '-' + time_str.replace('日', '日 ').replace('月', '-').replace('日', '-') + ':00'
        else:
            return ''
    except:
        return ''
