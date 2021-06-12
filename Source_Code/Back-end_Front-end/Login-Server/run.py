from flask import Flask
from flask import Response, request
from flask_restful import Resource, Api
from flask_jwt_extended import *
from json import dumps

import bcrypt
import pymysql
from config import Config


app = Flask(__name__)
api = Api(app)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = Config.key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.access
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.refresh

jwt = JWTManager(app)

class SignUp(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data['email']
        hashed_pwd = json_data['pwd'] = bcrypt.hashpw(
            json_data['pwd'].encode('UTF-8'), bcrypt.gensalt()  # str 객체, bytes로 인코드, salt를 이용하여 암호화
        )   
        company_name = json_data['company_name']
        category = json_data['category']
        user_name = json_data['user_name']
        phone_number = json_data['phone_number']
        company_reg_num = json_data['company_reg_num']

        sql = '''INSERT INTO users(email, hashed_pwd, company_name, category, user_name, phone_number, company_reg_num) 
                VALUES(%s, %s, %s, %s, %s, %s, %s)'''

        try:
            conn = pymysql.connect(**Config.config)
            cur = conn.cursor()
            cur.execute(sql, [email, hashed_pwd, company_name, category, user_name, phone_number, company_reg_num])
            conn.commit()

        except pymysql.IntegrityError:

            return Response(dumps({"message": "만들 수 없는 아이디입니다."}), status=200, mimetype='application/json')
        
        response_data = {
            "message": "생성되었습니다.",
            'user_name': user_name +"님"
        }
        return Response(dumps(response_data), status=201, mimetype='application/json')


class Login(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data['email']
        pwd = json_data['pwd']

        sql = '''SELECT user_id, hashed_pwd, roles, user_name, category FROM users WHERE email=%s'''
        
        conn = pymysql.connect(**Config.config)
        cur = conn.cursor()

        cur.execute(sql, [email])
        row = cur.fetchone()

        if row == None:
            return Response(dumps({'message': "email이 틀렸어요."}), status=400, mimetype='application/json')
        
        else:
            if row and bcrypt.checkpw(pwd.encode('UTF-8'), row[1]):
                user_id = row[0]

                # payload = UserObject(user_id=user_id, roles=row[2])
                payload = {
                    "user_id": user_id, 
                    "roles": row[2],
                    "user_name" : row[3],
                    "category" : row[4]
                }

                response_data = {
                    "access_token" : create_access_token(identity=payload),
                    "refresh_token" : create_refresh_token(identity=payload)
                }

                return Response(dumps("msg : success"), headers=response_data, status=201, mimetype='application/json')

            else:
                return Response(dumps({'message': "비밀번호가 틀렸어요."}), status=401, mimetype='application/json')


api.add_resource(Login, '/login')
api.add_resource(SignUp, '/signup')


if __name__ == "__main__":
    app.run(host='0.0.0.0')