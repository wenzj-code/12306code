from  codePlatform import  CJYClient
# 12306登录用户名
userName = '1111@qq.com'
# 12306密码
password = '1111'
# 超级鹰打码平台
chaoJiYing = CJYClient('你的超级鹰平台账户', '你的超级鹰平台密码','896970')
# 验证码图片路径
captchaFilePath = 'captcha.jpg'
# 车站电报码路径
stationCodesFilePath = 'stationsCode.txt'
# 座位类型，订票下单时需要传入
noSeat            = 'WZ' #无座
firstClassSeat    = 'M'  #一等座
secondClassSeat   = 'O'  #二等座
advancedSoftBerth = '6'  #高级软卧 A6
hardBerth         = '3'  #硬卧 A3
softBerth         = '4'  #软卧 A4
moveBerth         = 'F'  #动卧
hardSeat          = '1'  #硬座 A1
businessSeat      = '9'  #商务座 A9

#目标地址
dstStationAddr=('电白','马踏')
#目标车次
dstStationNo=('G6238','G6238')
#目标时间段,8点到9点
dstTime=('8','9')
#选择购买车票类型
#WZ无座,F动卧,M一等座,O二等座,1硬座,3硬卧,4软卧,6高级软卧,9商务座，0 不限
seatType=('O','1')
