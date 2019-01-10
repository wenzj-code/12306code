import re
from utility import Utility
from urllib import parse
from APIs import API
from queryTicket import LeftTicket
from login import Login



class BookTicket(object):

    def __init__(self):
        self.session = Login.session

    def bookTickets(self,username):
        queryData, trainDicts = LeftTicket().queryTickets()
        # 这个地方座位类型也是不是固定的，如硬卧有时候是3，有时是A3
        seatType = input('请输入车票类型,WZ无座,F动卧,M一等座,O二等座,1硬座,3硬卧,4软卧,6高级软卧,9商务座:\n')
        i = 0
        for trainDict in trainDicts:
            if trainDict[seatType]== Utility.greenColor('有') or trainDict[seatType].isdigit():
                print('为您选择的车次为{},正在为您抢票中……'.format(Utility.redColor(trainDict['trainName'])))
                self.submitOrderRequest(queryData,trainDict)
                self.getPassengerDTOs(seatType,username,trainDict)
                return
            else:
                i += 1
                if i >=len(trainDicts):  # 遍历所有车次后都未能查到座位，则打印错误信息
                    print(Utility.redColor('Error:系统未能查询到{}座位类型存有余票'.format(seatType)))
                continue

    def submitOrderRequest(self, queryData, trainDict):
        data = {
            'purpose_codes'          : 'ADULT',
            'query_from_station_name': queryData['fromStation'],
            'query_to_station_name'  : queryData['toStation'],
            'secretStr'              : parse.unquote(trainDict['secretStr']),
            'tour_flag'              : 'dc',
            'train_date'             : queryData['trainDate'],
            'undefined'              : ''
        }
        print('data:',data)
        rsp = self.session.post(API.submitOrderRequest, data=data)
        print(rsp)
        print(rsp.text)
        dict = rsp.json()
        if dict['status']:
            print('系统提交订单请求成功')
        elif dict['messages'] != []:
            if dict['messages'][0] == '车票信息已过期，请重新查询最新车票信息':
                print('车票信息已过期，请重新查询最新车票信息')
        else:
            print("系统提交订单请求失败")


    def initDC(self):
        # step 1: initDc
        data = {
            '_json_att': ''
        }
        res = self.session.post(API.initDc, data=data)
        try:
            repeatSubmitToken = re.findall(r"var globalRepeatSubmitToken = '(.*?)'", res.text)[0]
            keyCheckIsChange = re.findall(r"key_check_isChange':'(.*?)'", res.text)[0]
            # print('key_check_isChange:'+ key_check_isChange)
            return repeatSubmitToken,keyCheckIsChange
        except:
            print('获取Token参数失败')
            return


    def getPassengerDTOs(self,seatType,username,trainDict):

        # step 1: initDc
        repeatSubmitToken, keyCheckIsChange = self.initDC()

        # step2 : getPassengerDTOs

        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        res = self.session.post(API.getPassengerDTOs, data=data)
        passengers = res.json()['data']['normal_passengers']

        for passenger in passengers:
            if passenger['passenger_name'] == username:
                # step 3: Check order
                self.checkOrderInfo(seatType, repeatSubmitToken, passenger)
                # step 4:获取队列
                self.getQueueCount(seatType, repeatSubmitToken, keyCheckIsChange, trainDict, passenger)
                return
            else:
                print('无法购票')


    def checkOrderInfo(self,seatType,repeatSubmitToken,passenger):

        passengerTicketStr = '{},{},{},{},{},{},{},N'.format(seatType, passenger['passenger_flag'],
                                                                    passenger['passenger_type'],
                                                                    passenger['passenger_name'],
                                                                    passenger['passenger_id_type_code'],
                                                                    passenger['passenger_id_no'],
                                                                    passenger['mobile_no'])

        oldPassengerStr = '{},{},{},1_'.format(passenger['passenger_name'], passenger['passenger_id_type_code'],
                                                  passenger['passenger_id_no'])
        data = {
            '_json_att'          : '',
            'bed_level_order_num': '000000000000000000000000000000',
            'cancel_flag'        : '2',
            'oldPassengerStr'    : oldPassengerStr,
            'passengerTicketStr' : passengerTicketStr,
            'randCode'           : '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken,
            'tour_flag'          : 'dc',
            'whatsSelect'        : '1'
        }

        res = self.session.post(API.checkOrderInfo, data=data)
        dict = res.json()
        if dict['data']['submitStatus']:
            print('系统校验订单信息成功')
            if dict['data']['ifShowPassCode'] == 'Y':
                print('需要再次验证')
                return True
            if dict['data']['ifShowPassCode'] == 'N':
                return False
        else:
            print('系统校验订单信息失败')
            return False

    def getQueueCount(self,seatType,repeatSubmitToken,keyCheckIsChange,trainDict,passenger):

        data = {
            '_json_att'           : '',
            'fromStationTelecode' : trainDict['fromTelecode'],
            'leftTicket'          : trainDict['leftTicket'],
            'purpose_codes'       : '00',
            'REPEAT_SUBMIT_TOKEN' : repeatSubmitToken,
            'seatType'            : seatType,
            'stationTrainCode'    : trainDict['trainName'],
            'toStationTelecode'   : trainDict['toTelecode'],
            'train_date'          : Utility.getTrainDate(trainDict['trainDate']),
            'train_location'      : trainDict['trainLocation'],
            'train_no'            : trainDict['trainNumber'],
        }

        res = self.session.post(API.getQueueCount,data= data)


        if res.json()['status']:
            print('系统获取队列信息成功')
            self.confirmSingleForQueue(seatType,repeatSubmitToken,keyCheckIsChange,passenger,trainDict)

        else:
            print('系统获取队列信息失败')
            return


    def confirmSingleForQueue(self,seatType,repeatSubmitToken,keyCheckIsChange,passenger,trainDict):

        passengerTicketStr = '{},{},{},{},{},{},{},N'.format(seatType, passenger['passenger_flag'],
                                                             passenger['passenger_type'],
                                                             passenger['passenger_name'],
                                                             passenger['passenger_id_type_code'],
                                                             passenger['passenger_id_no'],
                                                             passenger['mobile_no'])

        oldPassengerStr = '{},{},{},1_'.format(passenger['passenger_name'], passenger['passenger_id_type_code'],
                                               passenger['passenger_id_no'])

        data = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldPassengerStr,
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': keyCheckIsChange,
            'leftTicketStr': trainDict['leftTicket'],
            'train_location': trainDict['trainLocation'],
            'choose_seats': '',
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken,
        }

        res = Login.session.post(API.confirmSingleForQueue, data= data)
        if res.json()['status']['submitStatus'] == 'true':
            print('已完成订票，请前往12306进行支付')
        else:
            print('订票失败,请稍后重试!')
