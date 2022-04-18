"""
Raspberry Pi Pico (MicroPython) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""
import machine
import utime

apn ="povo.jp"
username=""
password=""
writeKey = "***your writeKey***"
readKey = "***your readKey***"
channelID  = 12345 #your channelID

# uart setting
uart_port = 0
uart_baute = 115200
Pico_SIM7080G = machine.UART(uart_port, uart_baute)

# LED indicator on Raspberry Pi Pico
led_pin = 25  # onboard led
led_onboard = machine.Pin(led_pin, machine.Pin.OUT)

# HTTP Get Post Parameter
http_get_server = ['http://ambidata.io', 'api/v2/channels/' +str(channelID) +'/data?readKey=' +str(readKey)]
http_post_server = ['http://ambidata.io', 'api/v2/channels/' + str(channelID) + '/data']

# debug
debug=False

def led_blink():
    for i in range(1, 3):
        led_onboard.value(1)
        utime.sleep(1)
        led_onboard.value(0)
        utime.sleep(1)
    led_onboard.value(0)

# Send AT command
def send_at(cmd, back, timeout=1500):
    rec_buff = b''
    Pico_SIM7080G.write((cmd + '\r\n').encode())
    prvmills = utime.ticks_ms()
    while (utime.ticks_ms() - prvmills) < timeout:
        if Pico_SIM7080G.any():
            rec_buff = b"".join([rec_buff, Pico_SIM7080G.read(1)])
    if rec_buff != '':
        if back not in rec_buff.decode():
            if 'ERROR' in rec_buff.decode():
                print(cmd + ' back:\t' + rec_buff.decode())
                return 0
            else:
                # Resend cmd
                rec_buff = b''
                rec_buff = send_at_wait_resp(cmd, back, timeout)
                if back not in rec_buff.decode():
                    print(cmd + ' back:\t' + rec_buff.decode())
                    return 0
                else:
                    return 1
        else:
            if debug:
                print(rec_buff.decode())
            return 1
    else:
        print(cmd + ' no responce\n')
        # Resend cmd
        rec_buff = send_at_wait_resp(cmd, back, timeout)
        if back not in rec_buff.decode():
            print(cmd + ' back:\t' + rec_buff.decode())
            return 0
        else:
            return 1


# Send AT command and return response information
def send_at_wait_resp(cmd, back, timeout=2000):
    rec_buff = b''
    Pico_SIM7080G.write((cmd + '\r\n').encode())
    prvmills = utime.ticks_ms()
    while (utime.ticks_ms() - prvmills) < timeout:
        if Pico_SIM7080G.any():
            rec_buff = b"".join([rec_buff, Pico_SIM7080G.read(1)])
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(cmd + ' back:\t' + rec_buff.decode())
        else:
            if debug:
                print(rec_buff.decode())
            
    else:
        print(cmd + ' no responce')
    # print("Response information is: ", rec_buff)
    return rec_buff


# Module startup detection
def check_start():
    # simcom module uart may be fool,so it is better to send much times when it starts.
    send_at("AT", "OK")
    utime.sleep(1)
    for i in range(1, 4):
        if send_at("AT", "OK") == 1:
            print('------SIM7080G is ready------\r\n')
            send_at("ATE1", "OK")
            break
        else:
            module_power()
            print('------SIM7080G is starting up, please wait------\r\n')
            utime.sleep(5)


def set_network():
    print("Setting to LTE mode:\n")
    send_at("AT+CFUN=0", "OK")
    send_at("AT+CNMP=38", "OK")  # Select LTE mode
    send_at("AT+CMNB=1", "OK")  # Select Cat-M mode
    send_at("AT+CFUN=1", "OK")
    utime.sleep(5)


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
            utime.sleep(5)
            continue
    send_at("AT+CSQ", "OK")
    send_at("AT+CPSI?", "OK")
    send_at("AT+COPS?", "OK")
    #get_resp_info = str(send_at_wait_resp("AT+CGNAPN", "OK"))
    # getapn = get_resp_info.split('\"')
    # print(getapn[1])
    #getapn1 = get_resp_info[get_resp_info.find('\"')+1:get_resp_info.rfind('\"')]
    # print(getapn1)
    if username :
        send_at('AT+CNCFG=0,1,"'+apn+'","'+username+'","'+password+'"', "OK")
    else :
        send_at('AT+CNCFG=0,1,"'+apn+'"', "OK")
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
                resp = (send_at_wait_resp('AT+SHREAD=0,'+str(get_pack_len), 'OK', 5000)).decode()
                get_json=resp[resp.rfind('[')+1:resp.rfind(']')]
                #self.send_at('AT+SHDISC', 'OK')
                #print(f"get json:{get_json}\n")
                return get_json
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
            #print(http_post_msg)
            send_at(http_post_msg, 'OK',1000)
            #send_at('AT+SHBOD?','OK')
            resp = str(send_at_wait_resp('AT+SHREQ=\"/'+http_post_server[1]+'\",3','OK', 8000))
            #print("resp is :", resp)
            try:
                get_status = int(resp[resp.rfind(',')-3:resp.rfind(',')])
                print(f"status :{get_status}\n")
                return get_status
            except ValueError:
                print("ValueError!\n")

        else:
            print("Send failed\n")

    else:
        print("HTTP connection disconnected, please check and try again\n")


# SIM7080G main program
led_blink()
check_start()
set_network()
check_network()
d1 = 0
while True :
    msg = '{"writeKey":"' + writeKey + '","d1":"' +str(d1)+ '"}'
    print(f"post json :{msg}")
    http_post(msg)
    utime.sleep(5)
    d1+=1
    get_json=http_get(d1)
    print(f"get json:{get_json}\n")