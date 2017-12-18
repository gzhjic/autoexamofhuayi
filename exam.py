#-*-coding:utf-8-*-


#////////////////////////////////////////////////////////////////////
#//                          _ooOoo_                               //
#//                         o8888888o                              //
#//                         88" . "88                              //
#//                         (| ^_^ |)                              //
#//                         O\  =  /O                              //
#//                      ____/`---'\____                           //
#//                    .'  \\|     |//  `.                         //
#//                   /  \\|||  :  |||//  \                        //
#//                  /  _||||| -:- |||||-  \                       //
#//                  |   | \\\  -  /// |   |                       //
#//                  | \_|  ''\---/''  |   |                       //
#//                  \  .-\__  `-`  ___/-. /                       //
#//                ___`. .'  /--.--\  `. . ___                     //
#//              ."" '<  `.___\_<|>_/___.'  >'"".                  //
#//            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
#//            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
#//      ========`-.____`-.___\_____/___.-`____.-'========         //
#//                           `=---='                              //
#//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
#         佛祖保佑       永无BUG     永不修改                  //
#//////////////////////////////////////////////////////////////////
import requests
import re


def getContent(url):
    r = requests.get(url)
    return r.content


def login_cme1(username, password):
    login_data = {
        'UserName': username,
        'Password': password,
        'loginType': 1
    }

    header_base = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'cme1.91huayi.com',
        'Referer': 'http://sso.91huayi.com/sso/login_all.ashx?username='+username+'&password='+password+'&loginType=1&from=91huayi',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    session = requests.session()

    print '开始登陆...'
    baseurl = 'http://cme1.91huayi.com/sso/login_v2.ashx'

    session.get(baseurl, headers=header_base, data=login_data)
    print '登陆成功...'
    #进入课程列表
    session.get("http://www.91huayi.com/", verify=False)

    print '获取课程id列表...'
    #获取学习记录中的课程cid
    content = session.get("http://cme1.91huayi.com/pages/cme.aspx#", verify=False)
    pattern1 = re.compile(r"<a href='\.\./pages/course.aspx\?cid=.*? title=.*? target=.*?>")
    match1 = re.findall(pattern1, content.text)
    #获取我的课堂中的课程cid
    pattern2 = re.compile(r'</span><a href="course.aspx\?cid=.*? target="_blank" class')
    match2 = re.findall(pattern2, content.text)

    cids = []
    #for c in match1:
    #    cids.append(get_cid1(c))
    for c in match2:
        cids.append(get_cid2(c))


    for count in range(5):
        #进入课程url http://cme1.91huayi.com/pages/course.aspx?cid=fe5c7575-0a41-47c4-b0c5-a8e83d2bd249
        print '进入第' + str(count + 1) + '堂课程'
        print cids[count]
        exam = session.post('http://cme1.91huayi.com/pages/course.aspx?cid=' + cids[count])

        #获取考试科目cid
        pattern3 = re.compile(r'<a href=\'\.\./course_ware/course_ware\.aspx\?cwid=.*?\' target="new_courseWare".class="f14blue"><img')
        match3 = re.findall(pattern3, exam.text)
        print '共有' + str(len(match3)) + '门考试'
        for i in range(len(match3)):
            print '---开始第' + str(i + 1) + '门考试'

            exam_content = session.post('http://cme1.91huayi.com/pages/exam.aspx?cwid=' + get_exam_cid(match3[i]))

            #选项name
            pattern4 = re.compile(r'<input id="gvQuestion_rb.*?type="radio" name="gvQuest.*?</label>')
            match4 = re.findall(pattern4, exam_content.text)

            #隐藏答案
            pattern5 = re.compile(r'<input type="hidden" name="gvQuestion.*? id="gvQuestion.*?value=".*?/>')
            match5 = re.findall(pattern5, exam_content.text)

            subjects = []
            answers = []

            for ia in range(5):
                subjects.append(match4[ia*4].split('"')[5])

            for ans in match5:
                answers.append(ans.split('"')[3] + ":" + ans.split('"')[7])

            pattern6 = re.compile(r'id="__VIEWSTATE" value=".*?/>')
            match6 = re.findall(pattern6, exam_content.text)

            pattern7 = re.compile(r'__EVENTVALIDATION" value=.*?/>')
            match7 = re.findall(pattern7, exam_content.text)

            pattern8 = re.compile(r'Hidden1" value=".*/>')
            match8 = re.findall(pattern8, exam_content.text)
            pattern9 = re.compile(r'Hidden2" value=".*/>')
            match9 = re.findall(pattern9, exam_content.text)
            pattern10 = re.compile(r'Hidden3" value=".*/>')
            match10 = re.findall(pattern10, exam_content.text)

            exam_result = {
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__VIEWSTATE':match6[0].split('"')[3],
                #'__VIEWSTATE':'',
                '__VIEWSTATEGENERATOR':'265B8D93',
                '__EVENTVALIDATION':match7[0].split('"')[2],
                #'__EVENTVALIDATION': '',
                'Hidden1':match8[0].split('"')[2],
                'Hidden2': match9[0].split('"')[2],
                'Hidden3': match10[0].split('"')[2],
                'btn_submit.x':'26',
                'btn_submit.y': '26'
            }

            for ib in range(5):
                exam_result[subjects[ib]] = answers[ib].split(':')[1]
                exam_result[answers[ib].split(':')[0]] = answers[ib].split(':')[1]


            r = session.post('http://cme1.91huayi.com/pages/exam.aspx?cid=' + get_exam_cid(match3[i]),data=exam_result)
            result = session.get('http://cme1.91huayi.com/pages/exam_result.aspx?cwid=' + get_exam_cid(match3[i]))
            #print result.text
    #考试url:http://cme1.91huayi.com/pages/exam.aspx?cwid=5c6bb5e6-c023-4bac-af70-a59400a72975
    #课程url:http://cme1.91huayi.com/pages/course.aspx?cid=b293cc1f-ee35-44c6-9d80-ac821443e244
    #http://cme1.91huayi.com/pages/exam_result.aspx?cwid=9bd0cc30-a990-4bda-bf91-a62400b44458
def get_cid1(content):
    #content = r"<a href='../pages/course.aspx?cid=fe5c7575-0a41-47c4-b0c5-a8e83d2bd249' title='不同类型髋关节骨坏死的临床特点' target=\"_blank\">"
    return content.split(' ')[1].split('\'')[1].split('=')[1].strip('\\')

def get_cid2(content):
    #</span><a href="course.aspx?cid=b293cc1f-ee35-44c6-9d80-ac821443e244" target="_blank" class
    return content.split(' ')[1].split('=')[2].strip('"').strip('\\')
def get_exam_cid(content):
    return content.split(' ')[1].split('=')[2].strip('\'')

#在此处输入账号密码
login_cme1('username','password')
#str1= '\u4e0d\u540c\u7c7b\u578b\u9acb\u5173\u8282\u9aa8\u574f\u6b7b\u7684\u4e34\u5e8a\u7279\u70b9'
#print str1.decode('unicode_escape')
