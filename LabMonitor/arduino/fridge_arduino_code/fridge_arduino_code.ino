
/*
connection:
  - water: 
    - [pin 27] blue: Water Flow Sensor YF-B1
    - [pin 26] green: Pressure Sensor SEN0257
    - [pin 25] yellow: Temperature Sensor DS18B20
  - air:
    - [pin 14] Pressure Sensor
*/

#include <OneWire.h>
#include <DallasTemperature.h>

#define WATER_FLOW_PIN 27
#define WATER_PRES_PIN 26
#define WATER_TEMP_PIN 25
#define   AIR_PRES_PIN 14

#define WATER_PRES_OFFSET 0.5

volatile int counter = 0;
int oldTime = millis();
OneWire oneWire(WATER_TEMP_PIN);
DallasTemperature sensors(&oneWire);

void setup(){
  Serial.begin(115200);

  pinMode(WATER_FLOW_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(WATER_FLOW_PIN), onInterrupt, RISING);
}

void loop(){
  int newTime = millis();
  if(newTime - oldTime > 1000){
    // water flow
    float freq = counter / (newTime - oldTime);
    float flow = freq / 11; // L/min
    // water pres
    float water_volt = analogRead(WATER_PRES_PIN) * 3.3 / 4095; 
    float water_pres = (water_volt - WATER_PRES_OFFSET) * 400; // kPa
    // water temp
    sensors.requestTemperatures(); 
    float temp = sensors.getTempCByIndex(0); // C
    // air pres

    say("flow",flow); say("water_pres",water_pres); say("temp",temp); Serial.print('\n');
    // reset
    counter = 0;
    oldTime = newTime;
  }
}

void say(char key[], float val){
  Serial.print(key); Serial.print(':'); Serial.print(val); Serial.print(',');  
}

void onInterrupt(){
  counter++;
}
