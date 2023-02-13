import tools.Mek_master as master
from server.database import Token, BookMark


def testtokenftime():
    """查询全部token失效时间"""
    for t in Token.select():
        print(t.text, master.from_unix_time(t.Ftime)[1])




def clear_books():
    BookMark.delete()
