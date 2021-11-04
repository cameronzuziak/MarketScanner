import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import DataParser
from joblib import *
import multiprocessing
from tkinter import *
from tkinter.ttk import Combobox
 
# default values
MONTHS = 1
DAYS = 1
STD_DEV = 1
VARIABLE = 'Volume'
CURRENT_DATE = datetime.datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")

class MainClass:

    def bubble_sort(self, list_in):
        global VARIABLE
        n = len(list_in)
        for i in range(n-1):
            for j, obj in enumerate(list_in):
                if j < n-1:
                    if int(float(obj[VARIABLE])) > int(float(list_in[j+1][VARIABLE])):
                        list_in[j], list_in[j+1] = list_in[j+1], list_in[j]

    def set_values(self, metric, day, month, std):
        global STD_DEV
        global DAYS
        global MONTHS
        global VARIABLE
        STD_DEV = int(std)
        DAYS = int(day)
        MONTHS = int(month)
        VARIABLE = metric
        self.start_scan()

    # boolean for options
    def has_options(self, tick):
        opt = True
        try:
            x = yf.Ticker(tick)
            if x.options is not None:
                opt = True
                return opt
        except:
            opt = False
        return opt

    def get_data(self, ticker):
        global MONTHS
        currentDate = datetime.date.today() + datetime.timedelta(days=1)
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=MONTHS)
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
        sys.stdout = sys.__stdout__
        return data[[VARIABLE]]

    def get_outliers(self, data):
        global STD_DEV
        indxs = []
        outliers = []
        stnd = np.std(data[VARIABLE])
        mean = np.mean(data[VARIABLE])
        anomaly_cut_off = stnd * STD_DEV
        upper_limit = mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        for i in range(len(data)):
            temp = data[VARIABLE].iloc[i]
            if temp > upper_limit:
                indxs.append(str(data['Date'].iloc[i])[:-9])
                outliers.append(temp)
        d = {'Dates': indxs, VARIABLE: outliers}
        return d

    def append_new_line(file_name, text_to_append):
        with open(file_name, "a+") as file_object:
            file_object.seek(0)
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            file_object.write(text_to_append)

    def data_output(self, data, tick):
        string_out = tick.upper()
        for i in range(len(data['Dates'])):
            string1 = str(data['Dates'][i])
            string2 = str(data[VARIABLE][i])
            string_out = string_out + " | " + string1 + " " + VARIABLE + ": " + string2
        print(string_out)

    def get_valid_stocks(self, tick, currentDate, positive_scans):
        global DAYS
        data = (self.get_outliers(self.get_data(tick)))
        if data['Dates']:
            for i in range(len(data['Dates'])):
                dayStart = datetime.datetime.strptime(str(currentDate)[:-9], "%Y-%m-%d")
                dayEnd = datetime.datetime.strptime(str(data['Dates'][i]), "%Y-%m-%d")
                if abs((dayStart - dayEnd).days) <= DAYS and self.has_options(tick):
                    stocks = dict()
                    stocks['Ticker'] = tick
                    stocks['TargetDate'] = data['Dates'][0]
                    stocks[VARIABLE] = str('{:.2f}'.format(data[VARIABLE][0]))
                    positive_scans.append(stocks)
                    self.data_output(data, tick)

    def get_variable_value(self, dic):
        global VARIABLE
        return int(dic[VARIABLE])

    def start_scan(self):
        global DAYS
        global CURRENT_DATE
        global VARIABLE
        parser = DataParser(True)
        tickers = parser.get_list()
        jobs = multiprocessing.cpu_count()
        manager = multiprocessing.Manager()
        valid_stocks = manager.list()
        with parallel_backend('loky', n_jobs=jobs):
            Parallel()(delayed(self.get_valid_stocks)(tick, CURRENT_DATE, valid_stocks) for tick in tickers)
        valid_picks = open("stocks/validstockpics.txt", 'w')
        sorted_list = list(valid_stocks)
        self.bubble_sort(sorted_list)
        for dic in sorted_list:
            valid_picks.write(dic['Ticker'] + " | " + VARIABLE + ": " + dic[VARIABLE] + " - " + dic['TargetDate'])
            valid_picks.write("\n")
        valid_picks.close()
        print(valid_stocks)
        print(sorted_list)
        return valid_stocks


    def home_panel(self):
        panel_1 = PanedWindow(bd=4, relief="raised", bg="#00ffee")
        panel_1.pack(fill=BOTH, expand=1)

        metric_choices = ['Open', 'Close', 'High', 'Low', 'Volume']

        metric_select = Combobox(panel_1, width=20, values=metric_choices)
        metric_select.place(relx=.6, rely=0.1, anchor=CENTER)

        label = Label(panel_1,
                      text="Choose Metric",
                      anchor="e",
                      bg='#00ffee',
                      fg='white',
                      font="Helvetica 16 bold").place(relx=.3, rely=0.1, anchor=CENTER)
        myLabel = Label(panel_1,
                        text="Enter Month Range",
                        anchor="e",
                        bg='#00ffee',
                        fg='white',
                        font="Helvetica 16 bold").place(relx=.3, rely=0.3, anchor=CENTER)
        myLabel1 = Label(panel_1,
                         text="Enter Day Range",
                         anchor="e",
                         bg='#00ffee',
                         fg='white',
                         font="Helvetica 16 bold").place(relx=.3, rely=0.5, anchor=CENTER)
        myLabel2 = Label(panel_1,
                         text="Enter Standard Deviations",
                         anchor="e",
                         bg='#00ffee',
                         fg='white',
                         font="Helvetica 16 bold").place(relx=.3, rely=.7, anchor=CENTER)

        e = Entry(panel_1)
        e.place(relx=.6, rely=0.3, width=40, anchor=CENTER)
        e1 = Entry(panel_1)
        e1.place(relx=.6, rely=0.5, width=40, anchor=CENTER)
        e2 = Entry(panel_1)
        e2.place(relx=.6, rely=.7, width=40, anchor=CENTER)

        button5 = Button(panel_1, text="Run", width=15, activebackground='#00ff00', command=lambda *args:
        self.set_values(metric_select.get(), e1.get(), e.get(), e2.get())).place(relx=.4, rely=.9)

        return panel_1

    def __init__(self):
        pass

if __name__ == '__main__':
    window = Tk()
    window.geometry("600x400")
    MainClass().home_panel()
    window.mainloop()
