from video import Video
from os import path
from cv2.data import haarcascades
import socket
import json
import net
import time
import cv2
from _thread import *
import paho.mqtt.client as mqtt

CLIENT_HOST = '15.161.17.179'
# HOST = '15.161.17.179'
# PORT = 5000
door_topic='input/#'

state = False

client = mqtt.Client()

def detect_face(frame):
  face_xml = path.join(haarcascades, 'haarcascade_frontalface_default.xml')
  face_cascade = cv2.CascadeClassifier(face_xml)

  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  face = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(0,0))
  if len(face) == 0:
    return 0
  else:
    faces = face.shape[0]
    if faces > 0:
      num_detections = faces
      return num_detections


def show_image(data):
  cv2.imshow('frame', data)
  cv2.waitKey(0.5)

def server_adurl(reader):
    request = net.receive(reader)[0]
    if len(request) > 0:
        request = json.loads(request.decode())
        url = request['url']                   # url 주소
        filename = request['ad_file']
        if url == '0':
          print('detected nothing')
          return False
        # file_dir = f'C:/iot_workspace/project/input/video/ad_video/{filename}'
        file_dir = f'/home/pi/iot_workspace/project/output/ad_video/{filename}'
      
        if path.isfile(file_dir) == True:
          Video.video_play(file_dir)
        else:
          Video.connect_url(url, filename)                  # url 접속 후 영상 다운로드
          print('video start')
          Video.video_play(file_dir)                        # file 실행


def get_state():
  return state

def set_state(s):
  global state
  state = s


def camera(ip, port):
  global state

  print('camera enter')
  # state = True
  start_time = time.time()    # 시작 시간
  need_second = 3
  print(ip, port)
  dataset = []
  location = '도곡동-1'
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip, port))
    writer = s.makefile('wb')
    reader = s.makefile('rb')
    writer1 = s.makefile('wb')
    with Video(device = 0) as v:    # 카메라 번호 지정
    # with Video(file = 'test_people.jpg') as v:    # 카메라 번호 지정
      num_detections, image_data = 0, []
      for i in range(4):
        v.cap.read()
      middle_time = time.time()
      image = v
      for image in v:
        # Video.show(image)                       # 영상 스트리밍   - 추후 제거
        num_detection = detect_face(image)      # 검출 인원 수 체크
        # print(num_detection)
        if time.time() - middle_time > need_second:
          break         # 지정된 n초 후 break
        elif num_detection == 0:
          continue

        if num_detection > num_detections:
          num_detections = num_detection        # 최대로 인원 수 갱신
          image_data = Video.to_jpg(image)   # jpg파일 압축
      

      if len(image_data) == 0:                    # 이미지가 없으면
        print('no data')
      else:
        # dataset.append(image_data, location)
        # print("Number of faces detected: ", num_detections)
        net.send(writer, image_data)            # 서버로 데이터 전송
        net.send_str(writer1, location)            # 서버로 데이터 전송
        send_time = time.time()    # 전송 끝나는 시간

        print('img send ', len(image_data), '/', 'people :', num_detections)
        print('전송 작업시간 :', send_time - start_time)

        server_adurl(reader)                    # URL 수신

    end_time = time.time()    # 전송 끝나는 시간
    print('전체 시간 : ', end_time - start_time)
  state = False
  print('camera exit', state)

# if __name__ == '__main__':
#   print('start client...')
#   # start_new_thread(subscribe, (HOST, door_topic))
#   vclient(HOST, PORT, camera)
