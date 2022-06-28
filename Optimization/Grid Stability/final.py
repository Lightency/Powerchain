from decision import *
from numpy import *
from pandas import *
from influxdb import *
from relays import *

#read frequency and voltage measurmenets from csv file

measurements = read_csv(r"C:\Users\USER\Desktop\Work docs\openems\openems-dev\freq_volt.csv")
frequency=measurements['Frequency'].tolist()
voltage=measurements["Voltage"].tolist()

#get peak period
[peak,mid_peak,off_peak]=peak_period()

#Run algo and get decision
[increase,inc_val,decrease,dec_val,minimize,min_val] = stability(frequency,voltage,peak,mid_peak,off_peak)

#Run relay function
if increase:
    relay_opt(inc_val,increase,decrease,minimize)
elif decrease:
    relay_opt(dec_val,increase,decrease,minimize)
else:
    relay_opt(min_val,increase,decrease,minimize)



