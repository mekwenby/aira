import datetime
import time

import tools.Mek_master as Mek_master


def passwdc(l=4, cl='sha'):
    if cl == 'sha':
        passwd = Mek_master.get_random_hax(l)
    elif cl == 'uuid':
        passwd = Mek_master.get_uuid4()
    elif cl == 'letters':
        passwd = Mek_master.get_random_letters(l)
    elif cl == 'numbe':
        passwd = Mek_master.get_random_numbe(l)
    else:
        passwd = Mek_master.get_uuid4()

    return passwd


def strencrypt(str, cl):
    if cl == 'md5':
        return Mek_master.get_string_MD5(str)
    elif cl == 'sha1':
        return Mek_master.get_string_SHA(str)
    elif cl == 'sha256':
        return Mek_master.get_string_SHA256(str)
    elif cl == 'base64decode':
        # 字符串base64解码
        return Mek_master.base64decode(str)
    elif cl == 'base64encode':
        # 字符串base64编码
        try:
            return Mek_master.base64encode(str)
        except:
            return None

    else:
        return Mek_master.get_string_MD5(str)


# 计算时间天数差函数，精确到秒
def time_delta(time_start, time_end):
    date_time_start = time.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    date_time_end = time.strptime(time_end, "%Y-%m-%d %H:%M:%S")
    date_time_start = time.mktime(date_time_start)
    date_time_end = time.mktime(date_time_end)
    date_time_delta = date_time_end - date_time_start
    time_delta_min = int(date_time_delta / 60)
    return time_delta_min


def stringtime_to_unix(s):
    # 字符串时间转unix
    print(s)
    date_time_start = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M")
    unix_time = time.mktime(date_time_start.timetuple())
    return int(unix_time)


def passwd_sha1(passwd):
    """密码md5 加密"""
    key = 'MTM1MmNFN0JCQUU4MjQwYzNFNmVGRTIxQkI2YjJmQkUwN0VlMTY2OTU='
    p = Mek_master.get_string_MD5(key + passwd)
    return p


if __name__ == '__main__':
    print(passwd_sha1('123456'))
