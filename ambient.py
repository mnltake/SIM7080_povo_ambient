#!/usr/bin/python3

"""
Raspberry Pi  (Python3) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""
import RPi.GPIO as GPIO
import serial
import time

Pico_SIM7080G  = serial.Serial('/dev/ttyAMA0',115200)
Pico_SIM7080G .flushInput()


apn ="povo.jp"
writeKey = "***your writeKey***"
readKey = "***your readKey***"
channelID  = 12345 #your channelID



# HTTP Get Post Parameter
http_get_server = ['http://ambidata.io', 'api/v2/channels/' +str(channelID) +'/data?readKey=' +str(readKey)]
http_post_server = ['http://ambidata.io', 'api/v2/channels/' + str(channelID) + '/data']



# Send AT command
def send_at(command, back, timeout=1500):
	rec_buff = ''
	Pico_SIM7080G.write((command+'\r\n').encode())
	time.sleep(timeout*0.001)
	if Pico_SIM7080G.inWaiting():
		time.sleep(0.1 )
		rec_buff = Pico_SIM7080G.read(Pico_SIM7080G.inWaiting())
	if rec_buff != '':
		if back not in rec_buff.decode():
			print(command + ' ERROR')
			print(command + ' back:\t' + rec_buff.decode())
			return 0
		else:
			print(rec_buff.decode())
			return 1
	else:
		print(command + ' no responce')


# Send AT command and return response information
def send_at_wait_resp(command, back, timeout=2000):
    rec_buff = b''
    Pico_SIM7080G.write((command + '\r\n').encode())
    time.sleep(timeout*0.001)
    if Pico_SIM7080G.inWaiting():
        time.sleep(0.1 )
        rec_buff = Pico_SIM7080G.read(Pico_SIM7080G.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(command + ' ERROR')
            print(command + ' back:\t' + rec_buff.decode())
            return rec_buff
        else:
            print(rec_buff.decode())
            return rec_buff
    else:
        print(command + ' no responce')
    return rec_buff


# Module startup detection
def check_start():
    # simcom module uart may be fool,so it is better to send much times when it starts.
    send_at("AT", "OK")
    time.sleep(1)
    for i in range(1, 4):
        if send_at("AT", "OK") == 1:
            print('------SIM7080G is ready------\r\n')
            send_at("ATE1", "OK")
            break
        else:

            print('------SIM7080G is starting up, please wait------\r\n')
            time.sleep(5)


def set_network():
    print("Setting to LTE mode:\n")
    send_at("AT+CFUN=0", "OK")
    send_at("AT+CNMP=38", "OK")  # Select LTE mode
    send_at("AT+CMNB=1", "OK")  # Select Cat-M mode
    send_at("AT+CFUN=1", "OK")
    time.sleep(5)


# Check the network status
def check_network():
    if send_at("AT+CPIN?", "READY") != 1:
        print("------Please check whether the sim card has been inserted!------\n")
    for i in range(1, 10):
        if send_at("AT+CGATT?", "1"):
            print('------SIM7080G is online------\r\n')
            break
        else:
            print('------SIM7080G is offline, please wait...------\r\n')
            time.sleep(5)
            continue
    send_at("AT+CSQ", "OK")
    send_at("AT+CPSI?", "OK")
    send_at("AT+COPS?", "OK")
    #get_resp_info = str(send_at_wait_resp("AT+CGNAPN", "OK"))
    # getapn = get_resp_info.split('\"')
    # print(getapn[1])
    #getapn1 = get_resp_info[get_resp_info.find('\"')+1:get_resp_info.rfind('\"')]
    # print(getapn1)
    send_at("AT+CNCFG=0,1,\""+apn+"\"", "OK")
    if send_at('AT+CNACT=0,1', 'ACTIVE'):
        print("Network activation is successful\n")
    else:
        print("Please check the network and try again!\n")
    send_at('AT+CNACT?', 'OK')


def at_test():
    print("---------------------------SIM7080G AT TEST---------------------------")
    while True:
        try:
            command_input = str(input('Please input the AT command,press Ctrl+C to exit:\000'))
            send_at(command_input, 'OK', 2000)
        except KeyboardInterrupt:
            print('\n------Exit AT Command Test!------\r\n')
            module_power()
            print("------The module is power off!------\n")
            break

# Set HTTP body and head length

def set_http_length(bodylen,headerlen=350):
    send_at('AT+SHCONF=\"BODYLEN\",' + str(bodylen), 'OK',100)
    send_at('AT+SHCONF=\"HEADERLEN\",' + str(headerlen), 'OK',100)


# Set HTTP header content
def set_http_content():
 #   send_at('AT+CASSLCFG=0,SSL,0','OK')
    send_at('AT+SHCHEAD', 'OK',100)
    send_at('AT+SHAHEAD=\"Content-Type\",\"application/json\"', 'OK',100)
#     send_at('AT+SHAHEAD=\"User-Agent\",\"curl/7.47.0\"', 'OK')
#     send_at('AT+SHAHEAD=\"Cache-control\",\"no-cache\"', 'OK')
#     send_at('AT+SHAHEAD=\"Connection\",\"keep-alive\"', 'OK')
#     send_at('AT+SHAHEAD=\"Accept\",\"*/*\"', 'OK')
#     send_at('AT+SHAHEAD?', 'OK',100)

# HTTP GET TEST
def http_get(n=1):
    print("HTTP GET \n") 
    send_at_wait_resp('AT+SHDISC', 'OK')
    send_at('AT+SHCONF="URL",\"'+http_get_server[0]+'\"', 'OK')
    #set_http_length(0)
    send_at('AT+SHCONN', 'OK', 3000)
    if send_at('AT+SHSTATE?', '1'):
        set_http_content()
        resp = str(send_at_wait_resp('AT+SHREQ=\"'+http_get_server[1]+'&n=' + str(n)+'\",1', 'OK',8000))
        #print("resp is :", resp)
        try:
            get_pack_len = int(resp[resp.rfind(',')+1:-5])
            if get_pack_len > 0:
                rcvdata = send_at_wait_resp('AT+SHREAD=0,'+str(get_pack_len), 'OK', 5000)
                #send_at('AT+SHDISC', 'OK')
                print(rcvdata.decode())
            else:
                print("HTTP Get failed!\n")
        except ValueError:
            print("ValueError!\n")
    else:
        print("HTTP connection disconnected, please check and try again\n")


# HTTP POST TEST
def http_post(http_post_msg):
    print("HTTP Post \n")
    send_at_wait_resp('AT+SHDISC', 'OK',100)
    send_at('AT+SHCONF="URL",\"' + http_post_server[0] + '\"', 'OK',100)
    bodylen = len(http_post_msg)
    set_http_length(bodylen)
    send_at('AT+SHCONN', 'OK', 3000)
    if send_at('AT+SHSTATE?', '1',100):
        set_http_content()
        send_at('AT+SHCPARA', 'OK',100)
        if send_at('AT+SHBOD=' + str(bodylen) +',10000', '>', 100) :
            print(http_post_msg)
            send_at(http_post_msg, 'OK',1000)
            #send_at('AT+SHBOD?','OK')
            resp = str(send_at_wait_resp('AT+SHREQ=\"/'+http_post_server[1]+'\",3','OK', 8000))
            #print("resp is :", resp)
            try:
                get_pack = int(resp[resp.rfind(',')+1:-5])
                #print(get_pack)
                if get_pack > 0:
                    send_at_wait_resp('AT+SHREAD=0,' + str(get_pack), 'OK', 3000)
                    send_at('AT+SHDISC', 'OK')
                else:
                    
                    send_at('AT+SHDISC', 'OK')
                    
            except ValueError:
                print("ValueError!\n")

        else:
            print("Send failed\n")

    else:
        print("HTTP connection disconnected, please check and try again\n")


# SIM7080G main program

check_start()
set_network()
check_network()
d1 = 0
while True:
    msg = '{"writeKey":"' + writeKey + '","d1":"' +str(d1)+ '"}'
    http_post(msg)
    time.sleep(10)
    http_get(n=1)
    d1+=1
