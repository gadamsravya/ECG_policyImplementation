import serial
import time
# import pandas as pd
import matplotlib.pyplot as plt
import neurokit2 as nk
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp
import time

def measure_rpeak_intervals(rpeak_value, prev_rpeak_value):
    
    print("Inside measure rpeak intervals")
    
    interval = 0
    prev_rpeak_value -= 300
    for val in rpeak_value:
        
        if val-prev_rpeak_value>100:
            print("NOT GOOD")
        else:
            print("GOOD")
        
        prev_rpeak_value = val
    
    
    return interval

# Connect to Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("ecgrawdata-e21fa28d3aed.json", scope)
client = gspread.authorize(credentials)


## Create a sheet for each new run
sheet_name = "ECGData"+str(time.ctime(time.time()))
sheet = client.create(sheet_name)
sheet.share('sdm10@iitbbs.ac.in', perm_type='user', role='writer')

sheet = client.open(sheet_name).sheet1

print("New Sheet Created")

ser = serial.Serial('/dev/ttyACM0',9600)  

t = 0
bpm_list = []
t_list = []
prev_value = -1

while True:  
# for val in data['val']:
    try:  
        read_serial=ser.readline()  
        try:
            bpm = read_serial.decode('utf-8').strip()
        except:
            bpm = '0'
#         print(str(bpm)+"**")
        if(bpm.isdigit()==0):
            bpm = '0'
        bpm_list.append(int(bpm))
        t = t + 1
        t_list.append(t%300)
        
        if t%300==0:
#             plt.plot(t_list[:-1], bpm_list[:-1])
            sheet.insert_row(bpm_list, int(t/300))
            _, rpeaks = nk.ecg_peaks(bpm_list, sampling_rate=250)
            plot = nk.events_plot(rpeaks['ECG_R_Peaks'], bpm_list)
            print(rpeaks['ECG_R_Peaks'])
            measure_rpeak_intervals(rpeaks['ECG_R_Peaks'], prev_value)
            
            plt.show()
            bpm_list.clear()
            t_list.clear()

    except KeyboardInterrupt:  

        print ("\nExiting.....")  

        break

