#-*- coding: utf-8 -*-
from os import stat
from tkinter.constants import DISABLED
from requests import get
from bs4 import BeautifulSoup

import tkinter as tk
from tkinter import ttk
from datetime import datetime

DEBUG = True

#버스정보를 얻어오기위한 URL 서비스키는 정식으로 받지않은 샘플키
#정식으로 하려면 서비스키 필요
url = "https://api.gbis.go.kr/ws/rest/busarrivalservice/station?serviceKey=1234567890&stationId="

#정류장 번호, 정류장 검색시 URL에서 참고하여 기입
station_list = {
    "하안사거리.7단지": "213000190",
    "하안사거리.12단지":    "213000103",
    "목감도서관.대명아파트":    "224000081",
}

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.time = tk.Text(self, height=1, width=50)
        #self.time.pack()

        self.station_text = tk.StringVar()
        self.station2 = ttk.Combobox(self, textvariable = self.station_text, width=20)
        self.station2['values'] = list(station_list.keys())
        self.station2.current(0)

        self.station = tk.Text(self, height=1, width=30)
        self.buslist = tk.Text(self, height=15, width=50)
        self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)

        self.time.grid(column=0, row=0, columnspan=2)
        self.station.grid(column=0, row=1, columnspan=1)
        self.station2.grid(column=1, row=1, columnspan=1)
        self.buslist.grid(column=0, row=2, columnspan=2)
        self.QUIT.grid(column=0, row=3, columnspan=2)

        # initial time display
        self.station2.bind("<<ComboboxSelected>>", self.onUpdate())
        #self.onUpdate()
        
    def onUpdate(self):
        try:
            station_id = station_list[self.station2.get()]
            print(station_id)
            response = get(url + station_id, verify=False)

            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser').msgbody
                buses = soup.find_all("busarrivallist")

                if DEBUG == True: print(datetime.now())
                time_text = "checking at {}.".format(datetime.now())
                self.time.delete('1.0', tk.END) # 데이터를 표시하기 전에 텍스트 위젯에 내용을 삭제함
                self.time.insert('1.0', time_text)

                if DEBUG == True: print("station id is {}".format(station_id))
                station_text = "station id is {}".format(station_id)
                self.station.delete('1.0', tk.END)
                self.station.insert('1.0', station_text)

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
        
        self.after(60000, self.onUpdate)

root = tk.Tk()
root.title('버스언제와')
root.geometry('400x300')
root.resizable(0, 0)
root.attributes('-topmost', 1)
root.attributes('-alpha', 0.8)

app = Application(master=root)
root.mainloop()
