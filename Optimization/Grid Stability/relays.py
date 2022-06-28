from influxdb import *
import requests
from urllib import response
from requests.auth import HTTPBasicAuth
import socket
socket.getaddrinfo('localhost',8080)


#get request for the status of the relay
def relay_status(relay_int):
    relay_id="relay"+str(relay_int)
    api_url="http://x:admin@localhost:8084/rest/channel/"+relay_id+"/_PropertyEnabled"
    response = requests.get(api_url,auth=HTTPBasicAuth('admin','admin'))
    if response.status_code == 404:
        return(0)
    else:
        return(1)

#turn relay(i) on / off
def relay_switch(ip_addr_edge,relay_id_int,enabled):

    api_url="http://x:admin@"+str(ip_addr_edge)+":8084/jsonrpc"
    relay_id="relay"+str(relay_id_int)

    if int(enabled) == 1:
        input={"method": "updateComponentConfig", "params": {
            "componentId": relay_id,
            "properties": [{
                "name": "enabled",
                "value": True }] }
                }
    else:
        input={"method": "updateComponentConfig",
              "params": {
                    "componentId": relay_id,
                    "properties": [{
                        "name": "enabled",
                        "value": False }] }
                }
    response=requests.post(api_url,json=input,auth=HTTPBasicAuth('admin','admin'))
    return(response.status_code)


#depending on the input, the function turns a relay(i) on / off to reach the wanted value for the load (percent)
def relay_opt(percent,increase,decrease,minimize):
    percentage = int(percent)
    relay_value = [40,20,20,20,20,10,10,10]
    relays_enabled = []
    sum = 0
    
    for i in range(1,9): #sum and activated relays
        enabled = relay_status(i)
        if enabled:
            relays_enabled = relays_enabled + [1]
            sum = sum + relay_value[i-1]
        else:
            relays_enabled = relays_enabled + [0]
        print("status is ",relays_enabled)
    
    
    if minimize:
        if percentage > sum:
            increase = True
        else:
            decrease = True
    
    if increase:
        value = percentage-sum
        for i in range(0,5):
            if value >= 40 and relays_enabled[0] == 0:
                relay_switch('localhost',1,1)
                relays_enabled[0]=1
                value=value-40
            elif value >= 20:
                if relays_enabled[i] == 0:
                    relay_switch('localhost',i+1,1)
                    relays_enabled[i]=1
                    value=value-20
        j = 5
        while value != 0 and j<= 7:
            if relays_enabled[j] == 0:
                relay_switch('localhost',j+1,1)
                relays_enabled[j]=1
                value=value-10
                j = j+1
            else:
                j = j+1
        print("result of increase",relays_enabled)
    
    if decrease: #it decreases the load to the percentage given
        value = sum-percentage
        for i in range(0,5):
            if value >= 40 and relays_enabled[0] == 1:
                relay_switch('localhost',1,0)
                relays_enabled[0]=0
                value=value-40
            elif value >= 20:
                if relays_enabled[i] == 1:
                    relay_switch('localhost',i+1,0)
                    relays_enabled[i]=0
                    value=value-20
        i = 5
        while value != 0:
            if relays_enabled[i] == 1:
                relay_switch('localhost',i+1,0)
                relays_enabled[i]=0
                value=value-10
                i = i+1
            else:
                i = i+1
    print("result of decrease",relays_enabled)
