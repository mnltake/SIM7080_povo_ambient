#include <Arduino.h>
#include "pico/stdlib.h"
#include "pico.h"
#include "AmbientGsm.h"
#define TINY_GSM_MODEM_SIM7080
#include <TinyGsmClient.h>
#define SerialMon Serial
#define SerialAT Serial1
TinyGsm        modem(SerialAT);
TinyGsmClient client(modem);

#define PERIOD 30
#define PWRPIN 14
unsigned int channelId = 100; // AmbientのチャネルID
const char* writeKey = "writeKey"; // ライトキー
Ambient ambient;
void modemPWR(){
  
  digitalWrite(PWRPIN,HIGH);
  delay(2000);
  digitalWrite(PWRPIN,LOW);
  delay(2000);
}
void setup() {
  SerialMon.begin(115200);
  SerialMon.println("Wait...");

  // Set GSM module baud rate
  SerialAT.setRX(1);
  SerialAT.setTX(0);
  SerialAT.begin(115200);
  delay(1000);
  pinMode(PWRPIN, OUTPUT);
  modemPWR();
  // Restart takes quite some time
  // To skip it, call init() instead of restart()
  SerialMon.println("Initializing modem...");
  modem.restart();
  //modem.init();

  // String modemInfo = modem.getModemInfo();
  // SerialMon.print("Modem Info: ");
  // SerialMon.println(modemInfo);

  SerialMon.print(F("waitForNetwork()"));
  while (!modem.waitForNetwork()) SerialMon.print(".");
  SerialMon.println(F(" Ok."));

  // SerialMon.print(F("gprsConnect(povo.jp)"));
  // modem.gprsConnect("povo.jp", "", "");
  // SerialMon.println(F(" done."));

  // SerialMon.print(F("isNetworkConnected()"));
  // while (!modem.isNetworkConnected()) SerialMon.print(".");
  // SerialMon.println(F(" Ok."));

  // SerialMon.print(F("My IP addr: "));
  // IPAddress ipaddr = modem.localIP();
  // SerialMon.println(ipaddr);

  ambient.begin(channelId, writeKey, &client); 
}

void loop(){
    unsigned long t = millis();
    float uptime;
    // 起動時間を送信する
    uptime = (float)millis()/1000;
    ambient.set(1, String(uptime).c_str());
    SerialMon.print("uptime :");
    SerialMon.println(uptime);
    modem.gprsConnect("povo.jp", "", "");
    while (!modem.isNetworkConnected()) SerialMon.print(".");
    SerialMon.print(F("My IP addr: "));
    IPAddress ipaddr = modem.localIP();
    SerialMon.println(ipaddr);
    SerialMon.println("connect");
    (ambient.send())? Serial.println("send ok") : Serial.println("send error");

    t = millis() - t;
    t = (t < PERIOD * 1000) ? (PERIOD * 1000 - t) : 1;
    delay(t);
}
