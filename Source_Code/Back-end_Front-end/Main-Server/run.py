from flask import Flask
from flask.helpers import url_for
from flask_jwt_extended import *
from json import dumps, loads
from flask import request, render_template, redirect, make_response, jsonify, send_file

from config import Config
import boto3
import requests
import consul

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = Config.key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.access
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.refresh

jwt = JWTManager(app)

client = consul.Consul(host='172.18.0.6', port=8500)


"""
    These attributes are also available

    file.filename               # The actual name of the file
    file.content_type
    file.content_length
    file.mimetype

"""
def uploadToS3(local_path, bucket, s3_path):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name='eu-south-1'
    )
    s3.Bucket(bucket).put_object(Body=local_path, Key=s3_path, ACL='public-read')


# 메인페이지
@app.route('/')
def index():
    if request.cookies.get("access_token_cookie"):
        access_token = request.cookies.get("access_token_cookie")
        
        roles = decode_token(access_token)['sub']['roles']
        user_name = decode_token(access_token)['sub']['user_name']

        loginCheck = True

        return render_template('home/index.html', user_name=user_name, loginCheck=loginCheck, roles=roles)

    else:      
        loginCheck = False

        return render_template('home/index.html', loginCheck=loginCheck)


# 관리자 페이지
@app.route('/admin', methods=['GET'])
def admin():
    if request.cookies.get("access_token_cookie"):
        access_token = request.cookies.get("access_token_cookie")

        roles = decode_token(access_token)['sub']['roles']
        user_name = decode_token(access_token)['sub']['user_name']

        loginCheck = True
        
        headers = {"Authorization": "Bearer " + (access_token if access_token else "")}

        serviceName = "get-server"
        # Consul address, port number
        service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
        service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

        # Local address, port number
        # service_address = '127.0.0.1'
        # service_port = 5003

        url = "http://{}:{}".format(service_address, service_port)

        get = requests.post(url + '/admin', headers=headers)

        if get.status_code == 201:
            check = True

            data = get.json()
            cnt = data['cnt']
            month = data['month']
            cpm = list(data["cpm"].values())
            cpm_key = list(data["cpm"].keys())
            revenue = list(data["revenue"].values())
            revenue_key = list(data["revenue"].keys())

            return render_template('home/admin.html', loginCheck=loginCheck, check=check, 
                                    revenue=revenue, roles=roles, user_name=user_name, 
                                    cpm=cpm, cnt=cnt, month=month, cpm_key=cpm_key, revenue_key=revenue_key)

    else:
        loginCheck = False

        return render_template('home/index.html', loginCheck=loginCheck)


# 마이페이지
@app.route('/mypage', methods=['GET', 'POST'])
def mypage():
    if request.cookies.get("access_token_cookie"):
        access_token = request.cookies.get("access_token_cookie")

        roles = decode_token(access_token)['sub']['roles']
        user_name = decode_token(access_token)['sub']['user_name']
        user_id = decode_token(access_token)['sub']['user_id']

        loginCheck = True
        
        headers = {"Authorization": "Bearer " + (access_token if access_token else "")}

        serviceName = "get-server"
        # Consul address, port number
        service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
        service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

        # Local address, port number
        # service_address = '127.0.0.1'
        # service_port = 5003

        url = "http://{}:{}".format(service_address, service_port)

        get = requests.post(url + '/mypage', headers=headers)

        if get.status_code == 201:
            check = True
            
            pie_data = get.json()

        else:
            check = False

            pie_data = {
                "cpm" : 0, "reach" : 0, "frequency" : 0,
                "ad_name" : " ", "cnt" : 0,
                "man" : 0, "woman" : 0,
                "age_2030" : 0, "age_4050" : 0,
                "age_2030m" : 0, "age_2030w" : 0, 
                "age_4050m" : 0, "age_4050w" : 0,
                "kids" : 0, "silver" : 0,
            }

        return render_template('home/mypage.html', loginCheck=loginCheck, 
                                roles=roles, user_name=user_name, pie_data=pie_data,
                                check=check, user_id=user_id)

    else:
        loginCheck = False

        return render_template('home/index.html', loginCheck=loginCheck)


# 광고 타겟정보 등록 페이지
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.cookies.get("access_token_cookie"):
        access_token = request.cookies.get("access_token_cookie")
        category = decode_token(access_token)['sub']['category']
        
        loginCheck = True
        
        headers = {"Authorization": "Bearer " + (access_token if access_token else "")}
        if request.method == 'POST' and request.get_json():
            json_data = request.get_json()

            serviceName = "upload-server"
            service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
            service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

            # Local address, port number
            # service_address = '127.0.0.1'
            # service_port = 5002

            url = "http://{}:{}".format(service_address, service_port)

            s3 = requests.post(url + '/upload', headers=headers, json=json_data)

            if s3.status_code != 201:
                return render_template('home/mypage.html', loginCheck=loginCheck)
            

            return render_template('home/upload.html', loginCheck=loginCheck, category=category)
        
        else:
            return render_template('home/upload.html', loginCheck=loginCheck, category=category)

    else:
        loginCheck = False

        return render_template('home/index.html', loginCheck=loginCheck)


# 광고파일 등록 페이지
@app.route('/s3', methods=['GET', 'POST'])
def upload_ad():
    if request.cookies.get("access_token_cookie"):
        access_token = request.cookies.get("access_token_cookie")
        loginCheck = True
        
        headers = {"Authorization": "Bearer " + (access_token if access_token else "")}

        if request.method == 'POST' and request.files['file']:
            file = request.files['file']
            ad_name = file.filename.strip('.mp4')

            serviceName = "upload-server"
            service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
            service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

            # Local address, port number
            # service_address = '127.0.0.1'
            # service_port = 5002

            url = "http://{}:{}".format(service_address, service_port)

            s3 = requests.post(url + '/s3', headers=headers, json={"ad_name" : ad_name})

            if s3.status_code != 201:
                return render_template('home/upload_ad.html', loginCheck=loginCheck)

            output = uploadToS3(file, Config.BUCKET_NAME, file.filename)    # S3 Upload
            print("File Upload!")

            return redirect(url_for('mypage', loginCheck=loginCheck))

        else:
            return render_template('home/upload_ad.html', loginCheck=loginCheck)

    else:
        loginCheck = False

        return render_template('home/index.html', loginCheck=loginCheck)


# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        json_data = request.get_json()

        serviceName = "login-server"
        service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
        service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

        # Local address, port number
        # service_address = '127.0.0.1'
        # service_port = 5001

        url = "http://{}:{}".format(service_address, service_port)

        login_res = requests.post(url + '/login', json=json_data)

        if login_res.status_code == 400:

            return jsonify({"check" : 400})
        
        elif login_res.status_code == 401:

             return jsonify({"check" : 401})

        else:
            access_token = login_res.headers['access_token']
            refresh_token = login_res.headers['refresh_token']
            
            response = make_response(render_template('accounts/login.html', 
                                                access_token=access_token, 
                                                refresh_token=refresh_token, 
                                                check=200))
            response.set_cookie("access_token_cookie", access_token)

            return response

    else:
        
        return render_template('accounts/login.html')


# 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        json_data = request.get_json()

        serviceName = "login-server"
        service_address = client.catalog.service(serviceName)[1][0]['ServiceAddress']
        service_port = client.catalog.service(serviceName)[1][0]['ServicePort']

        # Local address, port number
        # service_address = '127.0.0.1'
        # service_port = 5001

        url = "http://{}:{}".format(service_address, service_port)

        response = requests.post(url + '/signup', json=json_data)
        
        message = response.json()['message']

        return render_template('accounts/signup.html', message=message)

    else:
        return render_template('accounts/signup.html')


# 로그아웃
@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie("access_token_cookie")

    return response


@app.route('/map1')
def map1():
    return render_template('includes/ad1.html')

@app.route('/map2')
def map2():
    return render_template('includes/ad2.html')

@app.route('/map3')
def map3():
    return render_template('includes/ad3.html')

@app.route('/map4')
def map4():
    return render_template('includes/ad4.html')

@app.route('/map5')
def map5():
    return render_template('includes/ad5.html')

@app.route('/map6')
def map6():
    return render_template('includes/ad6.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')