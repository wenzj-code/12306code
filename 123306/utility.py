from datetime import datetime
from stationCodes import StationCodes
from color import Color
import time
import requests


class Utility(object):

    @classmethod
    def getSession(self):

        session = requests.session()  # 创建session会话

        session.headers = {

            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        # session.verify = False  # 跳过SSL验证
        return session

    @classmethod
    def redColor(self, str):
        return Color.red(str)

    @classmethod
    def greenColor(self, str):
        return Color.green(str)

    # 反转字典
    @classmethod
    def reversalDict(self, dict):
        return {v: k for k, v in dict.items()}

    # 将历时转化为小时和分钟的形式
    @classmethod
    def getDuration(self, timeStr):
        duration = timeStr.replace(':', '时') + '分'
        if duration.startswith('00'):
            return duration[4:]
        return duration

    # 获取一个时间是周几
    @classmethod
    def getWeekDay(self, date):
        weekDayDict = {
            0: '周一',
            1: '周二',
            2: '周三',
            3: '周四',
            4: '周五',
            5: '周六',
            6: '周天',
        }
        day = datetime.strptime(date, '%Y-%m-%d').weekday()
        return weekDayDict[day]

    # 转化日期格式
    @classmethod
    def getDateFormat(self, date):
        # date格式为2018-08-08
        print('date1:', date)
        dateList = date.split('-')

        month = dateList[1]
        if month.startswith('0'):
            month = month.replace('0', '')

        day = dateList[2]
        if day.startswith('0'):
            day = day.replace('0', '')
        print('date:',date,',month:',month,',day:',day)
        return '{}月{}日'.format(month, day)

    # 检查购票日期是否合理
    @classmethod
    def checkDate(self, date):

        localTime = time.localtime()

        localDate = '%04d-%02d-%02d' % (localTime.tm_year, localTime.tm_mon, localTime.tm_mday)

        # 获得当前时间时间戳
        currentTimeStamp = int(time.time())
        # 预售时长的时间戳
        deltaTimeStamp = '2505600'
        # 截至日期时间戳
        deadTimeStamp = currentTimeStamp + int(deltaTimeStamp)
        # 获取预售票的截止日期时间
        deadTime = time.localtime(deadTimeStamp)
        deadDate = '%04d-%02d-%02d' % (deadTime.tm_year, deadTime.tm_mon, deadTime.tm_mday)
        # print(Colored.red('请注意合理的乘车日期范围是:{} 至 {}'.format(localDate, deadDate)))

        # 判断输入的乘车时间是否在合理乘车时间范围内
        # 将购票日期转换为时间数组
        trainTimeStruct = time.strptime(date, "%Y-%m-%d")
        # 转换为时间戳:
        trainTimeStamp = int(time.mktime(trainTimeStruct))
        # 将购票时间修改为12306可接受格式 ，如用户输入2018-8-7则格式改为2018-08-07
        trainTime = time.localtime(trainTimeStamp)
        trainDate = '%04d-%02d-%02d' % (trainTime.tm_year, trainTime.tm_mon, trainTime.tm_mday)
        # 比较购票日期时间戳与当前时间戳和预售截止日期时间戳
        if currentTimeStamp <= trainTimeStamp and trainTimeStamp <= deadTimeStamp:
            return True, trainDate
        else:
            print(Colored.red('Error:您输入的乘车日期:{}, 当前系统日期:{}, 预售截止日期:{}'.format(trainDate, localDate, deadDate)))
            return False, None

    @classmethod
    def getDate(self, dateStr):
        # dateStr格式为20180801
        year = time.strptime(dateStr, '%Y%m%d').tm_year
        month = time.strptime(dateStr, '%Y%m%d').tm_mon
        day = time.strptime(dateStr, '%Y%m%d').tm_mday
        return '%04d-%02d-%02d' % (year, month, day)

    # 根据车站名获取电报码
    @classmethod
    def getStationCode(self, station):
        codesDict = StationCodes().getCodesDict()
        if station in codesDict.keys():
            return codesDict[station]

    # 输入出发地和目的地
    @classmethod
    def inputStation(self, str):
        station = input('{}：\n'.format(str))
        if not station in StationCodes().getCodesDict().keys():
            print(Colored.red('Error:车站列表里无法查询到{}'.format(station)))
            station = input('{}：\n'.format(str))
        return station

    # 输入乘车日期
    @classmethod
    def inputTrainDate(self):
        trainDate = input('请输入购票时间,格式为2018-01-01:\n')
        try:
            trainTimeStruct = time.strptime(trainDate, "%Y-%m-%d")
        except:
            print('时间格式错误，请重新输入')
            trainDate = input('请输入购票时间,格式为2018-01-01:\n')
        timeFlag, trainDate = Utility.checkDate(trainDate)
        if timeFlag == False:
            trainDate = input('请输入购票时间,格式为2018-01-01:\n')
            timeFlag, trainDate = Utility.checkDate(trainDate)
        return trainDate

    @classmethod
    def getTrainDate(self, dateStr):
        # 返回格式 Wed Aug 22 2018 00: 00:00 GMT + 0800 (China Standard Time)
        # 转换成时间数组
        timeArray = time.strptime(dateStr, "%Y%m%d")
        # 转换成时间戳
        timestamp = time.mktime(timeArray)
        # 转换成localtime
        timeLocal = time.localtime(timestamp)
        # 转换成新的时间格式
        GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
        timeStr = time.strftime(GMT_FORMAT, timeLocal)
        return timeStr
