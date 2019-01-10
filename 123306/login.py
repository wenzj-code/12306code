import const
import re
from utility import  Utility
from color import Color
from APIs import API


class Login(object):
    session = Utility.getSession()  # 创建session
    def __init__(self):
        self.session = Login.session

    # 获取验证码正确答案
    def getCaptchaAnswer(self):
        response= self.session.get(API.captchaImage)
        if response.status_code ==200:
            print('验证码图片请求成功')
            with open(const.captchaFilePath, 'wb') as f:
                f.write(response.content) # 写入文件
        else:
            print(Color.red('验证码图片下载失败, 正在重试...'))
            self.getCaptchaAnswer() #递归
        try:
            # img = open(const.captchaFilePath, 'rb').read() #读取文件图片
            # answerStr,cjyAnswerDict = const.chaoJiYing.PostPic(img, 9004)
            print('请输入验证码坐标代号：')
            code = input()
            write = code.split(',')
            codes = ''
            locate = {'1': '44,44,','2': '114,44,','3': '185,44,','4': '254,44,',
                      '5': '44,124,','6': '114,124,','7': '185,124,','8': '254,124,',
            }
            for i in write:
                codes += locate[i]
            return codes  #返回自己写的验证码信息
        except Exception as e:
            print(str(e))

    # 验证码验证
    def captchaCheck(self):
        # 手动验证
        answer = self.getCaptchaAnswer()
        data = {
            'login_site':'E',  # 固定的
            'rand': 'sjrand',  # 固定的
            'answer': answer   # 验证码对应的坐标字符串
        }
        result = self.session.post(API.captchaCheck,data=data).json()
        print(result)
        if result['result_code'] == '4':
            print('验证码验证成功')
        else:
            print(Color.red('Error:{}'.format(result['result_message'])))
            # 报错到打码平台
            self.captchaCheck()
            return

    # 以下是登录过程进行的相关请求
    def userLogin(self):
        # step 1: check验证码
        self.captchaCheck()

        # step 2: login
        loginData = {
            'username': const.userName,   # 12306用户名
            'password': const.password,   # 12306密码
            'appid': 'otn'                #固定
        }
        result = self.session.post(API.login, data=loginData).json()

        # step 3：checkuser
        data = {
            '_json_att': ''
        }
        checkUser_res = self.session.post(API.checkUser, data=data)
        # if checkUser_res.json()['data']['flag']:
        #     print("用户在线验证成功")
        # else:
        #     print('检查用户不在线，请重新登录')
        #     self.userLogin()
        #     return

        # step 4: uamtk
        data = {
            'appid':'otn'  # 固定
        }
        uamtk_res = self.session.post(API.uamtk,data= data)
        newapptk = uamtk_res.json()['newapptk']

        # step 5: uamauthclient
        clientData = {
            'tk':newapptk
        }
        uamauthclient_res = self.session.post(API.uamauthclient,data = clientData)
        username = uamauthclient_res.json()['username']

        # step 6: initMy12306
        html = self.session.get(API.initMy12306).text
        genderStr = re.findall(r'<div id="my12306page".*?</span>(.*?)</h3>',html,re.S)[0].replace('\n','').split('，')[0] # 获取称谓，如先生
        print("{}{},恭喜您成功登录12306网站".format(Utility.redColor(username),genderStr))
        return username  # 返回用户名，便于抢票时使用。当然一个12306账户里可能有多个常用乘客，我们也可以获取联系人列表，给其他人抢票