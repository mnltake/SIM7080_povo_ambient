#include <Arduino.h>
#include <M5StickC.h>
#include "AmbientGsm.h"
#define TINY_GSM_MODEM_SIM7080
#include <TinyGsmClient.h>
#define SerialMon Serial
#define SerialAT Serial1
TinyGsm        modem(SerialAT);
TinyGsmClient client(modem);

#define PERIOD 30

unsigned int channelId = 100; // AmbientのチャネルID
const char* writeKey = "writeKey"; // ライトキー
Ambient ambient;

void setup() {
  M5.begin();//default baud rate 115200
  M5.Lcd.setTextColor(WHITE);
  M5.Lcd.setRotation(3);
  M5.Lcd.setTextSize(2);
  delay(200);
  SerialMon.println("Wait...");

  // Set GSM module baud rate
  SerialAT.begin(115200, SERIAL_8N1, 33, 32);//M5StickC
  // SerialAT.begin(115200, SERIAL_8N1, 32, 26);//ATOM Lite
  delay(1000);

  // Restart takes quite some time
  // To skip it, call init() instead of restart()
  SerialMon.println("Initializing modem...");
  modem.restart();
  //modem.init();

  String modemInfo = modem.getModemInfo();
  SerialMon.print("Modem Info: ");
  SerialMon.println(modemInfo);

  SerialMon.print(F("waitForNetwork()"));
  while (!modem.waitForNetwork()) SerialMon.print(".");
  SerialMon.println(F(" Ok."));

  SerialMon.print(F("gprsConnect(povo.jp)"));
  modem.gprsConnect("povo.jp", "", "");
  SerialMon.println(F(" done."));

  SerialMon.print(F("isNetworkConnected()"));
  while (!modem.isNetworkConnected()) SerialMon.print(".");
  SerialMon.println(F(" Ok."));

  SerialMon.print(F("My IP addr: "));
  IPAddress ipaddr = modem.localIP();
  SerialMon.println(ipaddr);

  ambient.begin(channelId, writeKey, &client); 
}

void loop(){
    unsigned long t = millis();
    float uptime;
    // 起動時間を送信する
    uptime = (float)millis()/1000;
    ambient.set(1, String(uptime).c_str());
    
    modem.gprsConnect("povo.jp", "", "");
    while (!modem.isNetworkConnected()) SerialMon.print(".");
    SerialMon.print(F("My IP addr: "));
    IPAddress ipaddr = modem.localIP();
    SerialMon.println(ipaddr);
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(5,0);
    M5.Lcd.println(ipaddr);
    M5.Lcd.setCursor(5,40);
    M5.Lcd.printf("uptime:%.1f", uptime);
    SerialMon.println(" connect");
    (ambient.send())? Serial.println("send ok") : Serial.println("send error");

    t = millis() - t;
    t = (t < PERIOD * 1000) ? (PERIOD * 1000 - t) : 1;
    delay(t);
}
