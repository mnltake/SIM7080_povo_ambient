/*
 * ambient.h - Library for sending data to Ambient
 * Created by Takehiko Shimojima, April 21, 2016
 */
#ifndef AmbientGsm_h
#define AmbientGsm_h

#include "Arduino.h"
#define TINY_GSM_MODEM_SIM7080
#include <TinyGsmClient.h>


#define AMBIENT_WRITEKEY_SIZE 18
#define AMBIENT_READKEY_SIZE 18
#define AMBIENT_MAX_RETRY 5
#define AMBIENT_DATA_SIZE 24
#define AMBIENT_NUM_PARAMS 11
#define AMBIENT_CMNT_SIZE 64
#define AMBIENT_TIMEOUT 30000UL

#define AM_BLACK 1
#define AM_WHITE 8
#define AM_RED 9
#define AM_ORANGE 10
#define AM_YELLOW 11
#define AM_GREEN 12
#define AM_CYAN 13
#define AM_BLUE 14
#define AM_PURPLE 15
#define AM_PINK 16

class Ambient
{
public:

    Ambient(void);

    bool begin(unsigned int channelId, const char * writeKey, TinyGsmClient * c, const char * readKey = NULL, int dev = 0);
    bool set(int field,const char * data);
  bool set(int field, double data);
  bool set(int field, int data);
    bool clear(int field);
    bool setcmnt(const char * cmnt);

    bool send(uint32_t tmout = AMBIENT_TIMEOUT);
    int bulk_send(char * buf, uint32_t tmout = AMBIENT_TIMEOUT);
    bool read(char * buf, int len, int n = 1, uint32_t tmout = AMBIENT_TIMEOUT);
    bool delete_data(const char * userKey, uint32_t tmout = AMBIENT_TIMEOUT);
    bool getchannel(const char * userKey, const char * devKey, unsigned int & channelId, char * writeKey, int len, TinyGsmClient * c, uint32_t tmout = AMBIENT_TIMEOUT, int dev = 0);
    int status;

private:

    TinyGsmClient  * client;
    unsigned int channelId;
    char writeKey[AMBIENT_WRITEKEY_SIZE];
    char readKey[AMBIENT_READKEY_SIZE];
    int dev;
    char host[18];
    int port;

    struct {
        int set;
        char item[AMBIENT_DATA_SIZE];
    } data[AMBIENT_NUM_PARAMS];
    struct {
        int set;
        char item[AMBIENT_CMNT_SIZE];
    } cmnt;
    bool connect2host(uint32_t tmout = AMBIENT_TIMEOUT);
    int getStatusCode(void);
};

#endif // AmbientGsm_h
