import const
from stationCodes import StationCodes
from utility import Utility
from color import Color
from prettytable import PrettyTable
from login import Login
from APIs import API

class LeftTicket(object):
    def __init__(self):
        self.session = Login.session  # 还是那句话，使用同一个session

    def queryTickets(self):

        StationCodes.getAndSaveStationCodes(self.session) # 先判断电报码文件是否存在，不存在再下载保存
        queryData = self.getQueryData() # 获取trainDate,fromStationCode,toStationCode，fromStation和toStation

        parameters = {
            'leftTicketDTO.train_date'  : queryData['trainDate'],        # 日期，格式为2018-08-28
            'leftTicketDTO.from_station': queryData['fromStationCode'],  # 出发站电报码
            'leftTicketDTO.to_station'  : queryData['toStationCode'],    # 到达站电报码
            'purpose_codes'             : 'ADULT'  # 0X00是学生票
        }
        res = self.session.get(API.queryTicket,params = parameters)
        print(res)
        print('res:',res.json())
        trainDicts = self.getTrainInfo(res.json(), queryData)
        return queryData, trainDicts  # 返回查询数据和车次信息，便于下单时使用

    def getTrainInfo(self,result,queryData):
        trainDict = {}   # 车次信息字典
        trainDicts = []  # 用于订票
        trains = []      #用于在terminal里打印

        results = result['data']['result']
        maps = result['data']['map']

        for item in results:
            trainInfo = item.split('|')
            # for index, item in enumerate(trainInfo, 0):
            #     print('{}:\t{}'.format(index, item)
            if trainInfo[11] =='Y':

                trainDict['secretStr']       = trainInfo[0]

                trainDict['trainNumber']     = trainInfo[2]  #5l0000D35273

                trainDict['trainName']       = trainInfo[3]    # 车次名称，如D352

                trainDict['fromTelecode']    = trainInfo[6] #出发地电报码

                trainDict['toTelecode']      = trainInfo[7] # 出发地电报码

                trainDict['fromStation']     = maps[trainInfo[6]]  # 上海

                trainDict['toStation']       = maps[trainInfo[7]]  # 成都

                trainDict['departTime']      = Color.green(trainInfo[8])  # 出发时间

                trainDict['arriveTime']      = Color.red(trainInfo[9])    # 到达时间

                trainDict['totalTime']       = Utility.getDuration(trainInfo[10])  # 总用时

                trainDict['leftTicket']      = trainInfo[12]  # 余票

                trainDict['trainDate']       = trainInfo[13]  #20180822

                trainDict['trainLocation']   = trainInfo[15]  # H2

                # 以下顺序貌似也不是一直固定的，我遇到过代表硬座的几天后代表其他座位了
                trainDict[const.businessSeat]     = trainInfo[32]  # 商务座

                trainDict[const.firstClassSeat]   = trainInfo[31]  #一等座

                trainDict[const.secondClassSeat]  = trainInfo[30] #二等座

                trainDict[const.advancedSoftBerth]= trainInfo[21] #高级软卧

                trainDict[const.softBerth]        = trainInfo[23] #软卧

                trainDict[const.moveBerth]        = trainInfo[33]#动卧

                trainDict[const.noSeat]           = trainInfo[26]#无座

                trainDict[const.hardBerth]        = trainInfo[28]#硬卧

                trainDict[const.hardSeat]         = trainInfo[29]#硬座

                trainDict['otherSeat']            = trainInfo[22]#其他

                # 如果值为空，则将值修改为'--',有票则有字显示为绿色，无票红色显示
                for key in trainDict.keys():
                    if trainDict[key] == '':
                        trainDict[key] = '--'
                    if trainDict[key] == '有':
                        trainDict[key] = Color.green('有')
                    if trainDict[key] == '无':
                        trainDict[key] = Color.red('无')

                train = [Color.magenta(trainDict['trainName']) + Color.green('[ID]') if trainInfo[18] == '1' else trainDict['trainName'],
                         Color.green(trainDict['fromStation']) + '\n' + Color.red(trainDict['toStation']),
                         trainDict['departTime'] + '\n' + trainDict['arriveTime'],
                         trainDict['totalTime'], trainDict[const.businessSeat] , trainDict[const.firstClassSeat],
                         trainDict[const.secondClassSeat], trainDict[const.advancedSoftBerth], trainDict[const.softBerth],
                         trainDict[const.moveBerth], trainDict[const.hardBerth], trainDict[const.hardSeat], trainDict[const.noSeat],
                         trainDict['otherSeat']]

                # 直接使用append方法将字典添加到列表中，如果需要更改字典中的数据，那么列表中的内容也会发生改变，这是因为dict在Python里是object，不属于primitive
                # type（即int、float、string、None、bool)。这意味着你一般操控的是一个指向object（对象）的指针，而非object本身。下面是改善方法：使用copy()
                trains.append(train)
                trainDicts.append(trainDict.copy())# 注意trainDict.copy()

        self.prettyPrint(trains,queryData) # 按照一定格式打印
        return trainDicts

    def getQueryData(self):
        # trainDate = Utility.inputTrainDate()                  # 日期
        # fromStation = Utility.inputStation('请输入出发地')     # 出发地
        # toStation = Utility.inputStation('请输入目的地')       # 目的地
        trainDate = '2019-02-01'
        fromStation = '广州'
        toStation = '电白'
        fromStationCode = Utility.getStationCode(fromStation) # 出发地电报码
        toStationCode = Utility.getStationCode(toStation)     # 目的地电报码

        queryData = {
            'fromStation':fromStation,
            'toStation':toStation,
            'trainDate':trainDate,
            'fromStationCode':fromStationCode,
            'toStationCode':toStationCode
        }
        return queryData

    def prettyPrint(self,trains,queryData):

        header = ["车次", "车站", "时间", "历时", "商务座","一等座", "二等座",'高级软卧',"软卧", "动卧", "硬卧", "硬座", "无座",'其他']
        pt = PrettyTable(header)
        date = queryData['trainDate']
        print('date:',date)
        title = '{}——>{}({} {}),共查询到{}个可购票的车次'.format(queryData['fromStation'],queryData['toStation'],Utility.getDateFormat(date),Utility.getWeekDay(date),len(trains))
        print('date:', date)
        pt.title = Color.cyan(title)
        pt.align["车次"] = "l"  # 左对齐
        for train in trains:
            pt.add_row(train)
        print(pt)
