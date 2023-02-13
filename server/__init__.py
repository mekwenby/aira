import datetime
import time
from flask import Flask, request, render_template, redirect, make_response, g
from flask_bootstrap import Bootstrap4
from server.database import User, Token, BookMark, PasswdBox, PasswdGenerate, Schedule
import tools.Mek_master as master
import tools

app = Flask(__name__)
bootstrap = Bootstrap4(app=app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True


@app.template_filter('unix')
def md_to_html(unix):
    """自定义过滤器,unix时间转格式化时间"""
    return master.from_unix_time(unix)[1]


@app.template_filter('ico')
def get_ico(url):
    url_l = url.split('/')
    return f'{url_l[0]}//{url_l[2]}/favicon.ico'


@app.template_filter('ctabs')
def get_abs(i):
    time_start = master.from_unix_time(i)[1]
    time_end = master.get_localtime()
    date_time_start = time.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    date_time_end = time.strptime(time_end, "%Y-%m-%d %H:%M:%S")
    date_time_start = time.mktime(date_time_start)
    date_time_end = time.mktime(date_time_end)
    date_time_delta = date_time_end - date_time_start
    time_delta_min = int(date_time_delta / 60 / 60 / 24)
    return abs(time_delta_min)


@app.template_filter('ct')
def Time_calculation(unix):
    """自定义过滤器,unix时间转格式化时间"""
    time_start = master.from_unix_time(unix)[1]
    time_end = master.get_localtime()
    date_time_start = time.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    date_time_end = time.strptime(time_end, "%Y-%m-%d %H:%M:%S")
    date_time_start = time.mktime(date_time_start)
    date_time_end = time.mktime(date_time_end)
    date_time_delta = date_time_end - date_time_start
    time_delta_min = int(date_time_delta / 60 / 60 / 24)
    return time_delta_min

@app.template_filter('md5')
def get_md5(value):
    return f'm5{master.get_string_MD5(value)}'

# 请求前需要做什么操作
@app.before_request
def before_request():
    # 初始化全局上下文
    g.user = None
    g.ip = None
    ip = request.access_route[0] if request.access_route else request.remote_addr
    text = request.cookies.get('token')
    # 获取令牌
    t = Token.get_or_none(text=text)
    # 判断令牌有效期
    if t is not None and t.Ftime > int(time.time()):  # 令牌为空或者已失效
        user = User.get_or_none(t.link_id)
        g.ip = ip
        g.user = user


@app.route('/')
def hello_world():  # put application's code here
    ip = request.access_route[0] if request.access_route else request.remote_addr
    # print(ip)
    if g.user is None:
        '''user 为空定向到登录页面'''
        return redirect('/login')

    else:
        return redirect('/index')


@app.route('/index')
def index():
    if g.user is not None:
        '''user 为空定向到登录页面'''
        # 获取书签列表
        book_list = [book for book in BookMark.select().where(BookMark.link_id == g.user.id)]
        schedule_1 = [sch for sch in
                      Schedule.select().where(
                          (Schedule.link_id == g.user.id) & (Schedule.time > int(time.time())))
                          .order_by(Schedule.time).limit(1)]
        if len(schedule_1) > 0:
            schedule1 = schedule_1[0]
        else:
            schedule1 = 'None'

        return render_template('index.html', user=g.user, ip=g.ip, book_list=book_list, schedule=schedule1)
    else:
        return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'GET':
        '''GET请求时前往登录页面'''
        return render_template('login.html')

    elif request.method == 'POST':
        name = request.form.get('name')
        passwd = request.form.get('passwd')
        auto = request.form.get('auto')
        user = User.get_or_none(name=name)
        '''密码需要进行sha1转换'''
        if user is not None and tools.passwd_sha1(passwd) == user.passwd:
            '''user不为空且密码正确'''
            g.ip = request.access_route[0] if request.access_route else request.remote_addr
            responder = make_response(redirect('/index'))
            '''生成登录令牌'''
            token = master.get_random_hax(64)
            if auto == 'on':  # 自动登录开关

                # 设置令牌有效期
                Token.create(link_id=user.id, text=token, Ftime=int(time.time()) + 60 * 60 * 24 * 30)
                responder.set_cookie(key='token', value=token, max_age=60 * 60 * 24 * 30)

            else:
                Token.create(link_id=user.id, text=token, Ftime=int(time.time()) + 60 * 60 * 24)
                responder.set_cookie(key='token', value=token)

            return responder

        else:  # 登录失败
            div = '''<br>
                    <div class="alert alert-danger" role="alert">
                    用户名或密码错误!
                    </div>'''
            return render_template('login.html', msg=div)
    else:
        redirect('/login')


@app.route('/passwd')
def passwd():
    """密码管理器"""
    if g.user is not None:
        pb_list = [data for data in PasswdBox.select().where(PasswdBox.link_id == g.user.id)]
        return render_template('PASSWD.html', user=g.user, ip=g.ip, pb_list=pb_list)
    else:
        redirect('/login')


@app.route('/passwdc', methods=['GET', 'POST'])
def passwdc():
    """密码生成器"""
    if g.user is not None and request.method == 'GET':
        user_id = g.user.id
        # print(user_id)
        pg_list = [pg for pg in PasswdGenerate.select().where(PasswdGenerate.link_id == user_id).order_by(
            PasswdGenerate.Ctime.desc())]

        return render_template('Pgeneration.html', user=g.user, ip=g.ip, pg=None, pg_list=pg_list)
    if g.user is not None and request.method == 'POST':

        cl = request.form.get('class')
        length = request.form.get('length')
        text = request.form.get('text')
        passwd = tools.passwdc(cl=cl.lower(), l=int(length))

        pg = PasswdGenerate(user=cl, passwd=passwd, info=text, link_id=g.user.id)
        pg.save()
        user_id = g.user.id
        # print(user_id)
        pg_list = [pg for pg in PasswdGenerate.select().where(PasswdGenerate.link_id == user_id).order_by(
            PasswdGenerate.Ctime.desc())]

        return render_template('Pgeneration.html', user=g.user, ip=g.ip, pg=pg, pg_list=pg_list)
    else:
        redirect('/login')


@app.route('/pgdel/<ids>')
def pgdel(ids):
    """删除"""
    if g.user is not None:
        pg = PasswdGenerate.get_or_none(PasswdGenerate.id == ids)
        """判断资源是否属于该用户"""
        if pg is not None and pg.link_id == g.user.id:
            pg.delete_instance()
            return redirect('/passwdc')
        else:
            return redirect('/passwdc')
    else:
        return redirect('/')


@app.route('/sedel/<ids>')
def sedel(ids):
    if g.user is not None:
        se = Schedule.get_or_none(Schedule.id == ids)
        if se is not None and se.link_id == g.user.id:
            se.delete_instance()
            return redirect('/schedule')
        else:
            return redirect('/schedule')
    else:
        return redirect('/')


@app.route('/books')
def books():
    """书签管理页"""
    if g.user is not None:
        # print(g.user.id)
        book_list = [book for book in BookMark.select().where(BookMark.link_id == g.user.id)]
        # print(book_list)
        return render_template('books.html', user=g.user, ip=g.ip, book_list=book_list)

    else:
        redirect('/login')


@app.route('/addbooks', methods=['GET', 'POST'])
def addbooks():
    """添加书签"""
    if g.user is not None and request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        # print(g.user.id, url, name)
        BookMark.create(link_id=g.user.id, url=url, info=name)
        return redirect('/books')
    else:
        return redirect('/books')


@app.route('/addpasswdbox', methods=['GET', 'POST'])
def addpasswdbox():
    """添加账户和密码"""
    if g.user is not None and request.method == 'POST':
        name = request.form.get('name')
        user = request.form.get('user')
        name = name.replace(' ', '_')
        if name == '':
            name = 'r' + master.get_random_hax(6)

        _passwd = request.form.get('passwd')
        PasswdBox.create(passwd=_passwd, link_id=g.user.id, user=user, info=name)
        return redirect('/passwd')
    else:
        return redirect('/')


@app.route('/delpasswdbox/<ids>')
def delpasswdbox(ids):
    if g.user is not None:
        psb = PasswdBox.get_or_none(PasswdBox.id == ids)  # 查找出对象
        if psb is not None and psb.link_id == g.user.id:
            psb.delete_instance()
            return redirect('/passwd')
        else:
            return redirect('/passwd')
    else:
        return redirect('/')


@app.route('/delbooks')
def delbooks():
    if g.user is not None:
        bid = request.args.get('id')
        bk = BookMark.get_or_none(BookMark.id == bid)
        if bk is not None and bk.link_id == g.user.id:
            bk.delete_instance()
            return redirect('/books')
        else:
            return redirect('/books')
    else:
        return redirect('/books')


@app.route('/logout')
def logout():
    """注销"""
    responder = make_response(redirect('/'))
    responder.delete_cookie(key='token')
    return responder


@app.route('/sring', methods=['GET', 'POST'])
def sring():
    """字符串加密"""
    if g.user is not None and request.method == 'POST':
        text = request.form.get('text')
        cl = request.form.get('class')
        cl = cl.lower()  # 转换为小写
        s = tools.strencrypt(str=text, cl=cl)
        return render_template('String.html', user=g.user, ip=g.ip, s=s)

    elif g.user is not None and request.method == 'GET':
        return render_template('String.html', user=g.user, ip=g.ip)

    else:
        return redirect('/')


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if g.user is not None and request.method == 'POST':

        text = request.form.get('text')
        date_time = request.form.get('datetime')
        if date_time == '':  # 没有传递是时间时设置默认时间
            date_time = time.time()
        else:
            date_time = tools.stringtime_to_unix(date_time)
        # print('text=', text, 'time=', date_time)
        print(date_time)
        Schedule.create(link_id=g.user.id, text=text, time=date_time)

        return redirect('/schedule')

    elif g.user is not None and request.method == 'GET':
        schedule_list = [sch for sch in
                         Schedule.select().where(
                             Schedule.link_id == g.user.id).order_by(
                             Schedule.time.desc())]

        print(schedule_list)

        return render_template('schedule.html', user=g.user, ip=g.ip, schedule_list=schedule_list)
    else:
        return redirect('/')


@app.route('/application', methods=['GET', 'POST'])
def application():
    if request.method == 'GET':
        return render_template('application.html')

    elif request.method == 'POST':
        name = request.form.get('name')
        passwd = request.form.get('passwd')
        passwd2 = request.form.get('passwd2')

        if User.get_or_none(name=name) is None:

            if passwd == passwd2:
                # 注意密码sha1处理
                User.create(name=name, passwd=tools.passwd_sha1(passwd))

                div = '''<br>
                                    <div class="alert alert-danger" role="alert">
                                    注册成功！
                                    </div>'''
                return render_template('login.html', msg=div)
            else:
                div = '''<br>
                                                <div class="alert alert-danger" role="alert">
                                                    密码不一致！
                                                </div>'''
                return render_template('application.html', msg=div)

        else:
            div = '''<br>
                                <div class="alert alert-danger" role="alert">
                                用户名已被使用！
                                </div>'''
            return render_template('application.html', msg=div)


@app.route('/centre', methods=['GET', 'POST'])
def centre():
    if g.user is not None and request.method == 'POST':
        passwd = request.form.get('passwd')
        newpasswd = request.form.get('newpasswd')
        passwd2 = request.form.get('passwd2')
        # print(passwd, newpasswd, passwd2)
        if tools.passwd_sha1(passwd) == g.user.passwd:
            # print('原密码一致')
            if newpasswd == passwd2:
                # print('密码一致')
                g.user.passwd = tools.passwd_sha1(newpasswd)
                g.user.save()
                div = '''
                <div class="alert alert-success" role="alert">
                密码修改成功！
                </div>'''
                return render_template('centre.html', user=g.user, ip=g.ip, msg=div)
            else:
                div = '''
                            <div class="alert alert-danger" role="alert">
                                新密码与确认密码不一致!
                            </div>'''

                return render_template('centre.html', user=g.user, ip=g.ip, msg=div)
        else:
            div = '''
            <div class="alert alert-danger" role="alert">
                原密码不正确!
            </div>'''

            return render_template('centre.html', user=g.user, ip=g.ip, msg=div)
    elif g.user is not None and request.method == 'GET':
        return render_template('centre.html', user=g.user, ip=g.ip)

    else:
        return redirect('/')


@app.route('/cleantoken')
def cleantoken():
    if g.user is not None:
        try:
            Token.delete().where(Token.link_id == g.user.id).execute()
        except:
            print(f'{g.user.id}删除token异常!')
        return redirect('/logout')
    else:
        return redirect('/')


if __name__ == '__main__':
    pass
