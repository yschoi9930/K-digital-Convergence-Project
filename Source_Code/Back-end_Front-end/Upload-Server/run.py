from flask import Flask
from flask import Response, request
from flask_restful import Resource, Api
from flask_jwt_extended import *
from json import dumps
import pymysql
from config import Config


app = Flask(__name__)
api = Api(app)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = Config.key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.access
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.refresh

jwt = JWTManager(app)


class AdvertPost(Resource):
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        user_id = get_jwt_identity()['user_id']
        target_age = json_data['target_age']
        target_gender = json_data['target_gender']
        
        budget_bf = json_data['budget']
        if budget_bf.split(' ')[1] == '만원':
            budget = budget_bf.split(' ')[0]

        elif len(budget_bf.split(' ')) > 2:
            bu = budget_bf.split(' ')[0]
            get = budget_bf.split(' ')[2]
            budget = bu + get
        
        else:
            budget = budget_bf.split(' ')[0] + '0000'

        period = json_data['period']
        location = json_data['location']

        # return print('user_id : {}, age : {}, gender : {}, budget : {}, period : {}, location : {}'.format(user_id, target_age, target_gender, budget, period, location))

        sql = '''INSERT INTO advert(user_id, target_age, target_gender, budget, period, location) 
                VALUES(%s, %s, %s, %s, %s, %s)'''

        try:
            conn = pymysql.connect(**Config.config)
            cur = conn.cursor()
            
            cur.execute(sql, [user_id, target_age, target_gender, budget, period, location])
            conn.commit()

        except pymysql.IntegrityError:

            return Response(dumps({"message": "등록 할수 없습니다."}), status=200, mimetype='application/json')
        
        response_data = {
            "message": "등록되었습니다."
        }
        return Response(dumps(response_data), status=201, mimetype='application/json')


class S3Post(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()['user_id']
        ad_name = request.get_json()['ad_name']
        print(ad_name)
        sql_ad = '''SELECT MAX(ad_id) FROM advert WHERE user_id=%s'''
        sql_us = '''UPDATE advert SET ad_name=%s WHERE ad_id=%s'''

        try:
            conn = pymysql.connect(**Config.config)
            cur = conn.cursor()
            
            cur.execute(sql_ad, [user_id])
            ad_id = cur.fetchone()
            
            cur.execute(sql_us, [ad_name, ad_id])
            conn.commit()

        except pymysql.IntegrityError:

            return Response(dumps({"message": "등록 할수 없습니다."}), status=200, mimetype='application/json')

        response_data = {
            "message": "등록되었습니다.",
            'ad_name': ad_name
        }

        return Response(dumps(response_data), status=201, mimetype='application/json')



api.add_resource(AdvertPost, '/upload')
api.add_resource(S3Post, '/s3')


if __name__ == "__main__":
    app.run(host='0.0.0.0')