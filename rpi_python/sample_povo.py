#!/usr/bin/python3

"""
Raspberry Pi  (Python3) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""

import time
import sim7080G_http
apn ="povo.jp"
username=""
password=""
writeKey = "***your writeKey***"
readKey = "***your readKey***"
channelID  = 12345 #your channelID
sim=sim7080G_http.SIM7080G_HTTP('/dev/ttyAMA0',115200,debug=False)

sim.set_apn(apn,username, password)
sim.set_ambient(writeKey,readKey,channelID)
sim.check_start()
sim.set_network()
sim.check_network()
d1 = 0
while True :
    msg = '{"writeKey":"' + writeKey + '","d1":"' +str(d1)+ '"}'
    print(f"post json :{msg}")
    sim.http_post(msg)
    time.sleep(5)
    d1+=1
    get_json=sim.http_get(n=d1)
    print(f"get json:{get_json}\n")
    
