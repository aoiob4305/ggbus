#-*- coding: utf-8 -*-
#rev2
from requests import get
from bs4 import BeautifulSoup

import tkinter as tk
from tkinter import ttk
from datetime import datetime

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

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(columnspan=2, rowspan=2)
        self.createWidgets()

    def createWidgets(self):
        self.time_current = tk.Text(self, height=1, width=45)
        self.time_rest = tk.Text(self, height=1, width=5)

        self.station_current = tk.Text(self, height=1, width=30)
        self.station_text = tk.StringVar()
        self.station_selection = ttk.Combobox(self, textvariable = self.station_text, width=20)
        self.station_selection['values'] = list(station_list.keys())
        self.station_selection.current(0)    

        self.buslist = tk.Text(self, height=15, width=50)
        self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)

        WIDGET_EXPAND = tk.N+tk.S+tk.W+tk.E
        self.time_current.grid(column=0, row=0, columnspan=1, sticky=WIDGET_EXPAND)
        self.time_rest.grid(column=1, row=0, columnspan=1, sticky=WIDGET_EXPAND)
        self.station_current.grid(column=0, row=1, sticky=WIDGET_EXPAND)
        self.station_selection.grid(column=1, row=1, sticky=WIDGET_EXPAND)
        self.buslist.grid(column=0, row=2, columnspan=2, sticky=WIDGET_EXPAND)
        self.QUIT.grid(column=0, row=3, columnspan=2, sticky=WIDGET_EXPAND)

        # initial time display
        self.station_selection.bind("<<ComboboxSelected>>", self.onUpdate())
        self.onUpdateTimer()
        
    def onUpdateTimer(self):
        self.time_rest.delete('1.0', tk.END)
        self.time_rest.insert('1.0', self.time_rest_value)
        self.time_rest_value = self.time_rest_value - 1
        self.after(1000, self.onUpdateTimer)

    def onUpdate(self):
        try:
            station_id = station_list[self.station_selection.get()]
            print(station_id)
            response = get(url + station_id, verify=False)

            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser').msgbody
                buses = soup.find_all("busarrivallist")

                if DEBUG == True: print(datetime.now())
                time_text = "checking at {}.".format(datetime.now())
                self.time_current.delete('1.0', tk.END) # 데이터를 표시하기 전에 텍스트 위젯에 내용을 삭제함
                self.time_current.insert('1.0', time_text)

                if DEBUG == True: print("station id is {}".format(station_id))
                station_text = "station id is {}".format(station_id)
                self.station_current.delete('1.0', tk.END)
                self.station_current.insert('1.0', station_text)

                self.buslist.delete('1.0', tk.END)
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

                        self.buslist.insert(tk.CURRENT, businfo_text)
            else :
                if DEBUG == True: print("url couldn't loaded: %s" % (response.status_code)) 

        except Exception as e:
            if DEBUG == True:
                print("error occured...", e)
                exit()
            print(e)

        self.time_rest_value = 60
        self.after(60000, self.onUpdate)

root = tk.Tk()
root.title('버스언제와')
root.resizable(0, 0)
root.attributes('-topmost', 1)
root.attributes('-alpha', 0.8)

config = cp.ConfigParser()    
config.read('setting.cfg', encoding='utf-8')
url = config.get("URL", "url")
station_list = {
    config.get("STATION", "station1"): config.get("STATION", "station1_code"),
    config.get("STATION", "station2"): config.get("STATION", "station2_code"),
}

app = Application(master=root)
root.mainloop()