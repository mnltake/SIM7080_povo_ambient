#!/usr/bin/python3

"""
Raspberry Pi  (Python3) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""


class SIM7080G_HTTP:
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200,debug=False) :
        import serial
        import time
        self.time=time
        self.port=port
        self.baudrate=baudrate
        self.modem  = serial.Serial(self.port, self.baudrate)
        self.modem .flushInput()
        self.debug=debug
    
    def set_apn(self,apn,username="", password=""):
        self.apn = apn
        self.username = username
        self.password = password

    def set_ambient(self,writeKey,readKey,channelID):
        self.writeKey=writeKey
        self.readKey=readKey
        self.channelID=channelID
        # HTTP Get Post Parameter
        self.http_get_server = ['http://ambidata.io', 'api/v2/channels/' +str(self.channelID) +'/data?readKey=' +str(self.readKey)]
        self.http_post_server = ['http://ambidata.io', 'api/v2/channels/' + str(self.channelID) + '/data']



    # Send AT command
    def send_at(self,command, back, timeout=1.5):
        rec_buff = ''
        self.modem.write((command+'\r\n').encode())
        self.time.sleep(timeout)
        if self.modem.inWaiting():
            self.time.sleep(0.1 )
            rec_buff = self.modem.read(self.modem.inWaiting())
        if rec_buff != '':
            if back not in rec_buff.decode():
                print(command + ' ERROR')
                print(command + ' back:\t' + rec_buff.decode())
                return 0
            else:
                if self.debug:
                    print(rec_buff.decode())
                return 1
        else:
            print(command + ' no responce')
            return 0


    # Send AT command and return response information
    def send_at_wait_resp(self,command, back, timeout=1.5):
        rec_buff = b''
        self.modem.write((command + '\r\n').encode())
        self.time.sleep(timeout)
        if self.modem.inWaiting():
            self.time.sleep(0.1 )
            rec_buff = self.modem.read(self.modem.inWaiting())
        if rec_buff != '':
            if back not in rec_buff.decode():
                if self.debug:
                    print(command + ' ERROR')
                    print(command + ' back:\t' + rec_buff.decode())
                return rec_buff
            else:
                if self.debug:
                    print(rec_buff.decode())
                return rec_buff
        else:
            print(command + ' no responce')
        return rec_buff


    # Module startup detection
    def check_start(self):
        # simcom module uart may be fool,so it is better to send much times when it starts.
        self.send_at("AT", "OK")
        self.time.sleep(1)
        for i in range(1, 4):
            if self.send_at("AT", "OK") == 1:
                print('------SIM7080G is ready------\r\n')
                self.send_at("ATE1", "OK")
                return 1
            else:

                print('------SIM7080G is starting up, please wait------\r\n')
                self.time.sleep(5)
        return 0


    def set_network(self):
        print("Setting to LTE mode:\n")
        self.send_at("AT+CFUN=0", "OK")
        self.send_at("AT+CNMP=38", "OK")  # Select LTE mode
        self.send_at("AT+CMNB=1", "OK")  # Select Cat-M mode
        self.send_at("AT+CFUN=1", "OK")



    # Check the network status
    def check_network(self):
        if self.send_at("AT+CPIN?", "READY") != 1:
            print("------Please check whether the sim card has been inserted!------\n")
        for i in range(1, 10):
            if self.send_at("AT+CGATT?", "1"):
                print('------SIM7080G is online------\r\n')
                break
            else:
                print('------SIM7080G is offline, please wait...------\r\n')
                self.time.sleep(5)
                continue
        self.send_at("AT+CSQ", "OK")
        self.send_at("AT+CPSI?", "OK")
        self.send_at("AT+COPS?", "OK")
        # get_resp_info = str(self.send_at_wait_resp("AT+CGNAPN", "OK"))
        # getapn = get_resp_info.split('\"')
        # print(getapn[1])
        # getapn1 = get_resp_info[get_resp_info.find('\"')+1:get_resp_info.rfind('\"')]
        # print(getapn1)
        if self.username :
            self.send_at('AT+CNCFG=0,1,"'+self.apn+'","'+self.username+'","'+self.password+'"', "OK")
        else :
            self.send_at('AT+CNCFG=0,1,"'+self.apn+'"', "OK")
        if self.send_at('AT+CNACT=0,1', 'ACTIVE'):
            print("Network activation is successful\n")
        else:
            print("Please check the network and try again!\n")
        self.send_at('AT+CNACT?', 'OK')


    def at_test(self):
        print("---------------------------SIM7080G AT TEST---------------------------")
        while True:
            try:
                command_input = str(input('Please input the AT command,press Ctrl+C to exit:\000'))
                self.send_at(command_input, 'OK', 2)
            except KeyboardInterrupt:
                print('\n------Exit AT Command Test!------\r\n')
                print("------The module is power off!------\n")
                break

    # Set HTTP body and head length

    def set_http_length(self,bodylen,headerlen=350):
        self.send_at('AT+SHCONF=\"BODYLEN\",' + str(bodylen), 'OK',0.1)
        self.send_at('AT+SHCONF=\"HEADERLEN\",' + str(headerlen), 'OK',0.1)


    # Set HTTP header content
    def set_http_content(self):
    #   self.send_at('AT+CASSLCFG=0,SSL,0','OK')
        self.send_at('AT+SHCHEAD', 'OK',0.1)
        self.send_at('AT+SHAHEAD=\"Content-Type\",\"application/json\"', 'OK',0.1)
    #     self.send_at('AT+SHAHEAD=\"User-Agent\",\"curl/7.47.0\"', 'OK')
    #     self.send_at('AT+SHAHEAD=\"Cache-control\",\"no-cache\"', 'OK')
    #     self.send_at('AT+SHAHEAD=\"Connection\",\"keep-alive\"', 'OK')
    #     self.send_at('AT+SHAHEAD=\"Accept\",\"*/*\"', 'OK')
    #     self.send_at('AT+SHAHEAD?', 'OK',100)
    
    def close(self):
        self.send_at('AT+SHDISC', 'OK')

    # HTTP GET TEST
    def http_get(self,n=1):
        print("HTTP GET ") 
        self.send_at_wait_resp('AT+SHDISC', 'OK')
        self.send_at('AT+SHCONF="URL",\"'+self.http_get_server[0]+'\"', 'OK')
        #set_http_length(0)
        self.send_at('AT+SHCONN', 'OK', 3)
        if self.send_at('AT+SHSTATE?', '1'):
            self.set_http_content()
            resp = str(self.send_at_wait_resp('AT+SHREQ=\"'+self.http_get_server[1]+'&n=' + str(n)+'\",1', 'OK',8))
            #print("resp is :", resp)
            try:
                get_pack_len = int(resp[resp.rfind(',')+1:-5])
                if get_pack_len > 0:
                    resp = (self.send_at_wait_resp('AT+SHREAD=0,'+str(get_pack_len), 'OK', 5)).decode()
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
    def http_post(self,http_post_msg):
        print("HTTP POST ")
        self.send_at_wait_resp('AT+SHDISC', 'OK',0.1)
        self.send_at('AT+SHCONF="URL",\"' + self.http_post_server[0] + '\"', 'OK',0.1)
        bodylen = len(http_post_msg)
        self.set_http_length(bodylen)
        self.send_at('AT+SHCONN', 'OK', 3)
        if self.send_at('AT+SHSTATE?', '1',0.1):
            self.set_http_content()
            self.send_at('AT+SHCPARA', 'OK',0.1)
            if self.send_at('AT+SHBOD=' + str(bodylen) +',10000', '>', 0.1) :
                #print(f"post json :{http_post_msg}")
                self.send_at(http_post_msg, 'OK',1)
                #self.send_at('AT+SHBOD?','OK')
                resp = str(self.send_at_wait_resp('AT+SHREQ=\"/'+self.http_post_server[1]+'\",3','OK', 8))
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


