import threading
from _thread import *
import paho.mqtt.client as mqtt 
from camera import camera, state, set_state, get_state

SERVER_HOST = '15.161.17.179'
# SERVER_HOST = '192.168.1.47'
BROKER_HOST = '172.30.1.70'
PORT = 5001

door_topic='input/#'


# 브로커 접속 시도 결과 처리 콜백 함수
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        client.subscribe(door_topic)  # 연결 성공시 토픽 구독 신청
    else:
        print('연결 실패 : ', rc)


# 관련 토픽 메세지 수신 콜백 함수
def on_message(client, userdata, msg):
    global state
    print(state)
    print(msg.topic+" "+str(msg.payload))
    if msg.payload == b'detected':
        if get_state() == True: # 작업중
            print('카메라 작동중')
            pass
        else: # 대기상태
            set_state(True)
            start_new_thread(camera, (SERVER_HOST, PORT))


def input():
    print('start sub...')
    # 1. MQTT 클라이언트 객체 인스턴스화
    client = mqtt.Client()

    # 2. 관련 이벤트에 대한 콜백 함수 등록
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # 3. 브로커 연결
        client.connect(BROKER_HOST)

        # 4. 메세지 루프 - 이벤트 발생시 해당 콜백 함수 호출됨
        client.loop_forever()

    except Exception as err:
        print('에러 : %s' % err)
    except KeyboardInterrupt:
        print('수동 종료')


if __name__ == '__main__':
    # t_input = threading.Thread(target=input)
    # t_input.start()
    input()