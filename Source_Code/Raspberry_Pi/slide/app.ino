#include <MqttCom.h>
#include <Sensor.h>
#include <arduino.h>

const char *ssid = "TECH2_2G";
const char *password = "tech21234!";
const char *server =  "172.30.1.55";
// const char *ssid = "DO";
// const char *password = "ehtldud123";
// const char *server =  "192.168.0.10";
const char *pub_topic = "input/lift/switch";

MqttCom com(ssid, password);
Sensor sensor(D6);

void publishWorking() {
  com.publish("input/door/work", "working on");
}

ICACHE_RAM_ATTR void open_sensor(){
  com.publish(pub_topic, "open");
}
ICACHE_RAM_ATTR void close_sensor(){
  com.publish(pub_topic, "close");
}

void setup(){
  Serial.begin(115200);
  com.init(server);                         // publish만 실행
  com.setInterval(30000, publishWorking);   // 센서 작동 확인
  sensor.setCallback(close_sensor);       // 센서 감지 시 콜백
}

void check(){
  int value1 = digitalRead(D6);
  delay(10);
  int value2 = digitalRead(D6);
  if(value1 != value2 && value2 == 0){
    open_sensor();
  }
  else if(value1 != value2 && value2 == 1){
    close_sensor();
  }
}

void loop(){
  com.run();
  check();
}