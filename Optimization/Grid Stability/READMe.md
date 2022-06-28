The objective of this function is to stabilize the grid and keep the frequency and voltage at acceptable ranges.
When the Frequency or the voltage are out of range, the algorithm increases or decreases the load to stabilize them.

For the purpose of simulations, the loads are represented by 8 relays that are switchable (ON/OFF), each being a specific value of the load.

The algorithm should be something like this:

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



