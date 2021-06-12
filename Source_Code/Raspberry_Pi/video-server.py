import net
import json
import numpy as np
import cv2
import pymysql
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import random
from mtcnn.mtcnn import MTCNN
import matplotlib.image as img
import matplotlib.pyplot as plt
import time
from PIL import Image
import base64
from io import BytesIO
from keras import backend as K

# HOST = '172.30.1.55'
HOST = '172.31.25.76'
PORT = 5001

ix = 0

def receiver(client, addr):
    reader = client.makefile('rb')
    reader1 = client.makefile('rb')
    writer = client.makefile('wb')
    # try:
    data, data_len = net.receive(reader)
    location = net.receive_str(reader)
    print('received', data_len)  # 이미지 처리
    print(location)
    location = location.decode('cp949')
    print(location)
    data = np.frombuffer(data, dtype=np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    ai(data, writer, location)
    # except Exception as e:
    #     result = json.dumps({'url':'0', 'ad_file' : '0'})
    #     net.send(writer, result.encode())
    #     print('Error :', e)

    print('exit receiver')

def show_image(data):
    # byte 배열을 numpy로 변환
    data = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    cv2.imshow('frame', image)
    cv2.waitKey(1)


def face_crop(IoT_Input):
    detector = MTCNN()
    result_list = detector.detect_faces(IoT_Input)
    face_list = []
    for i in range(len(result_list)):
        result_list2 = []
        for v in result_list[i]['box']:
            if v >= 0:
                result_list2.append(v)
            else:
                result_list2.append(0)
        x1, y1, width, height = result_list2
        x2, y2 = x1 + width, y1 + height
        cropped = cv2.resize(IoT_Input[y1:y2, x1:x2], (128, 128))
        cropped = cropped.astype('float32')
        cropped /= 255.
        cropped = cropped.reshape(-1, 128, 128, 3)
        face_list.append(cropped)
    return face_list

# version_Loss_Fuction
def focal_loss(total_y_train, total_y_test):
     gamma = 2.0
     alpha = 0.25
     pt_1 = tf.where(tf.equal(total_y_train, 1), total_y_test, tf.ones_like(total_y_test))
     pt_0 = tf.where(tf.equal(total_y_train, 0), total_y_test, tf.zeros_like(total_y_test))
     return -K.sum(alpha * K.pow(1. - pt_1, gamma) * K.log(pt_1))-K.sum((1-alpha) * K.pow( pt_0, gamma) * K.log(1. - pt_0))

def load_models():
    model_age = keras.models.load_model('/home/ubuntu/ai/models/test_MN_age_model_128.h5')
    model_gender = keras.models.load_model('/home/ubuntu/ai/models/test_CNN_gender_Loss_model_128.h5', custom_objects={'focal_loss': focal_loss})

    return model_age, model_gender

def predict_models(model_age, model_gender, cropped_image):
    age_idx = 0
    age_result = ''
    gender_result = ''

    age = model_age.predict(cropped_image)  # [아동 2030 4050 실버]

    for i in range(len(age[0])):
        if age[0][i] == max(age[0]):
            age_idx = i

    if age_idx == 0:
        age_result = 'kids'
    elif age_idx == 1:
        age_result = '2030'
    elif age_idx == 2:
        age_result = '4050'
    else:
        age_result = 'silver'

    gender = model_gender.predict(cropped_image)  # 0 남자 1 여자
    if gender[0][0] > 0.5:
        gender_result = 'woman'
    else:
        gender_result = 'man'
    return age_result, gender_result


def select_AD(count_list):  # [kids, 2030M, 2030W, 4050M, 4050W, silver]
    conn = pymysql.connect(host='yangjae-team08-database.ca8iiefanafw.eu-south-1.rds.amazonaws.com',
                           port=3306, user='admin', password='yangjae8', db='mydb', charset='utf8')
    cur = conn.cursor()

    max_index = []
    count_max = max(count_list)
    ad_id_list = []
    CPM_list = []
    NULL_ad_id = []
    max_ad_id = []

    for i, n in enumerate(count_list):
        if n == count_max:
            max_index.append(i)

    for i in max_index:
        if i == 0:
            ad_id_list.append(2)
        elif i == 1:
            ad_id_list.append(3)
        elif i == 2:
            ad_id_list.append(4)
        elif i == 3:
            ad_id_list.append(1)
        elif i == 4:
            ad_id_list.append(6)
        else:
            ad_id_list.append(5)

    sql_CPM = '''SELECT ROUND(sub.cost / sub.cnt * 1000, 2) AS CPM
                FROM (SELECT ad.ad_id, ad.budget / ad.period AS cost, COUNT(t.ad_id) AS cnt
                    FROM advert ad LEFT JOIN target t 
                    ON ad.ad_id = t.ad_id
                    GROUP BY ad.ad_id, t.ad_id) sub
                WHERE sub.ad_id = %s
                GROUP BY sub.ad_id'''

    for id in ad_id_list:
        cur.execute(sql_CPM, id)
        cpm = cur.fetchone()
        CPM_list.append(cpm)

    for i in range(len(CPM_list)):
        if type(CPM_list[i][0]) != float:
            NULL_ad_id.append(ad_id_list[i])

    CPM_max = 0
    if len(CPM_list) != 0:
        for i in range(len(CPM_list)):
            if type(CPM_list[i][0]) == float and CPM_list[i][0] > CPM_max:
                CPM_max = CPM_list[i][0]
    if len(NULL_ad_id) == 0:
        temp_id = []
        for i in range(len(CPM_list)):
            if CPM_list[i][0] == CPM_max:
                temp_id.append(ad_id_list[i])
        if len(temp_id) == 1:
            return temp_id[0]
        else:
            selected_id = random.choice(temp_id)
            return selected_id
    elif len(NULL_ad_id) == 1:
        return NULL_ad_id[0]
    else:
        selected_id = random.choice(NULL_ad_id)
        return selected_id


def ai(data, writer, location):
    count_list = [0, 0, 0, 0, 0, 0]
    conn = pymysql.connect(host='yangjae-team08-database.ca8iiefanafw.eu-south-1.rds.amazonaws.com',
                           port=3306, user='admin', password='yangjae8', db='mydb', charset='utf8')
    cur = conn.cursor()
    tm = time.localtime((time.time()))
    data_date = f'{tm.tm_year}_{tm.tm_mon}_{tm.tm_mday}_{tm.tm_min}_{tm.tm_sec}'
    faces_list = []
    faces_list = face_crop(data)

    if len(faces_list) == 0:
        result = json.dumps({'url': '0', 'ad_file': '0'})
        net.send(writer, result.encode())
    else:
        model_age, model_gender = load_models()
        print('detected' + str(len(faces_list)))
        cam_location = location

        temp_age = []
        temp_gender = []
        temp_crop = []
        for i, face in enumerate(faces_list):
            buffer = BytesIO()
            age_result, gender_result = predict_models(model_age, model_gender, face)

            face = face.reshape(128, 128, 3)
            face_jpg = Image.fromarray((face * 255).astype(np.uint8))
            face_jpg.save(buffer, format='jpeg')
            face_byte = base64.b64encode(buffer.getvalue())

            if age_result == 'kids':
                count_list[0] += 1
            elif age_result == '2030' and gender_result == 'man':
                count_list[1] += 1
            elif age_result == '2030' and gender_result == 'woman':
                count_list[2] += 1
            elif age_result == '4050' and gender_result == 'man':
                count_list[3] += 1
            elif age_result == '4050' and gender_result == 'woman':
                count_list[4] += 1
            else:
                count_list[5] += 1

            temp_age.append(age_result)
            temp_gender.append(gender_result)
            temp_crop.append(face_byte)
        selected_id = select_AD(count_list)

        sql_select_AD = f'SELECT ad_id, ad_name FROM advert WHERE ad_id = "{selected_id}"'
        cur.execute(sql_select_AD)
        ad_id, ad_name = cur.fetchone()
        print('url')
        IoT_ad_url = f'https://yangjae-team08-bucket.s3.eu-south-1.amazonaws.com/{ad_name}.mp4'
        IoT_ad_url = IoT_ad_url.replace(' ', '+')
        IoT_ad_name = ad_name + '.mp4'
        IoT_ad_name = IoT_ad_name.replace(' ', '_')

        result = json.dumps({'url': IoT_ad_url, 'ad_file': IoT_ad_name})
        net.send(writer, result.encode())

        for crop, age, gender in zip(temp_crop, temp_age, temp_gender):
            # INSERT face Table
            sql_face = '''INSERT INTO face(face_array, input_image, location)
                    VALUES(%s, %s, %s)'''
            cur.execute(sql_face, [crop, data_date, cam_location])
            conn.commit()

            # MAX(face_id)
            sql_face_id = '''SELECT MAX(face_id) FROM face'''
            cur.execute(sql_face_id)
            face_id = cur.fetchone()

            # INSERT target Table SQL
            sql_target = '''INSERT INTO target(face_id, ad_id, age, gender)
                    VALUES(%s, %s, %s, %s)'''
            cur.execute(sql_target, [face_id, ad_id, age, gender])
            conn.commit()

if __name__ == '__main__':
    print('start server...')
    net.server(HOST, PORT, receiver)
