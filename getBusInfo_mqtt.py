#-*- coding: utf-8 -*-
#rev3
#mqtt 추가/gui 제거
from requests import get
from bs4 import BeautifulSoup

import paho.mqtt.client as mqtt

import configparser as cp

DEBUG = True

#버스정보를 얻어오기위한 URL 서비스키는 정식으로 받지않은 샘플키
#정식으로 하려면 서비스키 필요
#url = "https://api.gbis.go.kr/ws/rest/busarrivalservice/station?serviceKey=1234567890&stationId="

#정류장 번호, 정류장 검색시 URL에서 참고하여 기입
#station_list = {
#    "하안사거리.7단지": "213000190",
#    "하안사거리.12단지":    "213000103",
#    "목감도서관.대명아파트":    "224000081",
#}


def getBusInfo(station_id):
    try:
        print(station_id)
        response = get(url + station_id, verify=False)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')#.msgbody
            if DEBUG == True: print(soup.msgheader.resultcode.text)

            if soup.msgheader.resultcode.text == "0":
                buses = soup.msgbody.find_all("busarrivallist")

                station_text = "station id is {}".format(station_id)
                if DEBUG == True: print(station_text)

                for bus in buses:
                    bus_num = bus.routename.text
                    bus_predicttime_1 = bus.predicttime1.text
                    bus_predicttime_2 = bus.predicttime2.text

                    if bus_predicttime_1 != '':
                        businfo_text = "버스번호: {}\t첫번째: {}분\t두번째: {}분\n".format(
                            bus_num, 
                            bus_predicttime_1,
                            bus_predicttime_2
                            )

                        if DEBUG == True: print(businfo_text)
            else:
                print("버스정류장을 찾을 수 없습니다.")
                exit()
        else:
            if DEBUG == True: print("url couldn't loaded: %s" % (response.status_code)) 

    except Exception as e:
        if DEBUG == True:
            print("error occured...", e)
            exit()
        print(e)

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("connect ok")
    else:
        print("Bad connection Returned code =", rc)

def onDisconnect(client, userdata, flags, rc=0):
    print(str(rc))

def onPublish(client, userdata, mid):
    print("In on_pub callback mid=", mid)



config = cp.ConfigParser()    
config.read('setting.cfg', encoding='utf-8')
url = config.get("URL", "url")

getBusInfo(config.get("STATION", "station1_code"))
