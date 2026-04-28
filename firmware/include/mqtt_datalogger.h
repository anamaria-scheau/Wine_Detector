#ifndef MQTT_DATALOGGER_H
#define MQTT_DATALOGGER_H

#include "bme68xLibrary.h"
#include <sstream>
#include <iostream>
#include <PubSubClient.h>

class mqttDataLogger
{
private:
    std::stringstream _sensor_ss;
    PubSubClient *_client;
    const char *_topic;
    int _totalSensorCount;
    int _sensorCount;

    bool publishSensorData();

public:
    mqttDataLogger(PubSubClient *client, int totalSensorCount, const char *mqttTopic);
    void beginSensorData();
    void assembleAndPublishSensorData(const int sensorId, const bme68xData* bmeData);
};

#endif