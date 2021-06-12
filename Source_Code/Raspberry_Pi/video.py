import cv2
import numpy as np
import urllib.request
import subprocess as sp

class Video:
  def __init__(self, **kargs):
      device = kargs.get('device', -1)
      file = kargs.get('file')
      if device >= 0:
        self.cap = cv2.VideoCapture(device)
      elif file:
        self.cap = cv2.VideoCapture(file)

  def __iter__(self):
    return self
  
  def __next__(self):
    ret, image = self.cap.read()
    if ret:
      return image
    else:
      raise StopIteration

  def __enter__(self):
    return self

  def __exit__(self, type, value, trace_back):
    if self.cap and self.cap.isOpened():
      print('video release------')
      self.cap.release()

  @staticmethod
  def to_jpg(frame, quality=80):
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), quality]
    is_success, jpg = cv2.imencode(".jpg", frame, encode_param)
    return jpg
  
  @staticmethod
  def show (image, exit_char=ord('q')):
    cv2.imshow('frame', image)
    if cv2.waitKey(1) & 0xFF == exit_char:
      return False
    return True

  @staticmethod
  def  rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
  
  @staticmethod
  def resize_frame(frame, width, height):
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    
  @staticmethod
  def connect_url(url,filename):
    # Windows
    # chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'
    directory = f'/home/pi/iot_workspace/project/output/ad_video/{filename}'
    print(directory)
    print(filename)
    urllib.request.urlretrieve(url, directory)
    print(' 광고 저장 완료 ')
    return True
  
  # @staticmethod
  # def video_play(filename):
  #   cap = cv2.VideoCapture(filename)
  #   print('video play')
  #   while cap.isOpened():
  #     ret, frame = cap.read()
  #     if not ret:
  #       print("Don't find ad_file")
  #       break
  #     cv2.imshow(f'{filename}', frame)
  #     if cv2.waitKey(42) == ord('q'):
  #       break

  @staticmethod
  def video_play(filename):
    sp.run(['cvlc', filename])
    print('finish video')


if __name__ == '__main__':
  v = Video(device=0)
  for image in v:
    image = Video.resize_frame(image, 320, 240)
    # image = Video.resize_frame(image, 60)
    # jpg = Video.to_jpg(image)
    if not Video.show(image): break

# with open(file) as f:
