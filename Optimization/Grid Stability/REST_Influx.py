from influxdb import *
from urllib import response
import requests
from requests.auth import HTTPBasicAuth
import socket
socket.getaddrinfo('localhost',8080)

#get request
api_url="http://x:admin@localhost:8084/rest/channel/_appManager/DefectiveApp"
response = requests.get(api_url,auth=HTTPBasicAuth('admin','admin'))
respjson=response.json() #dict of 6 enteries, respjson['value'] gives you the value 
print(respjson)

#post request
api_url="http://x:admin@localhost:8084/jsonrpc"
input={"method": "updateComponentConfig", "params": {
		"componentId": "ctrlPeakShaving0",
		"properties": [{
 			"name": "enabled",
			"value": False }] } }
response=requests.post(api_url,json=input,auth=HTTPBasicAuth('admin','admin'))
print(response.json())

#connect to influx and extract data

client = InfluxDBClient(host='nope', port=8086, database='data')
result=client.query('SELECT "_cycle/State","_cycle/MeasuredCycleTime" FROM "data"')
jon=result.raw #dict
ser=jon['series'] #dict
data=[] #list of all inputs
data_length=len(ser[0]['values']) #number of inputs
length=len(ser[0]['values'])-1
for i in range(0,length):
    data=data+ser[0]['values'][i]

#the list data is structured this way: 'time','state','measuredTime' -> for example data[0] gives you the first time of insertion of data
# data[3] gives you the second time of insertion of data -> data[n modulo 3], n=0,1,2