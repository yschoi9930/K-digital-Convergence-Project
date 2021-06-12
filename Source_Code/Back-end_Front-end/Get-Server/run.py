from flask import Flask
from flask import Response, jsonify, request
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


class Mypage(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()['user_id']

        # 접속한 아이디가 등록한 광고를 시청한 성별
        sql_gender = '''SELECT ad.ad_name, t.gender, count(*) as cnt
                FROM target t LEFT JOIN advert ad ON ad.ad_id = t.ad_id
                WHERE t.ad_id in 
                (SELECT ad_id FROM advert WHERE user_id=%s)
                GROUP BY t.ad_id, t.gender
                ORDER BY t.ad_id, t.gender;'''
        
        # 접속한 아이디가 등록한 광고를 시청한 나이
        sql_age = '''SELECT  ad.ad_name, t.age, count(*) AS cnt
                FROM  target t LEFT JOIN advert ad ON ad.ad_id = t.ad_id
                WHERE t.ad_id in 
                (SELECT ad_id FROM advert WHERE user_id=%s)
                GROUP BY  t.ad_id, t.age
                ORDER BY t.ad_id, t.age;'''

        # 접속한 아이디가 등록한 광고를 시청한 타겟
        sql_target = '''SELECT ad_id, gender, age, count(*) as cnt
                FROM target
                WHERE ad_id in 
                (SELECT ad_id FROM advert WHERE user_id=%s)
                and age in ('2030', '4050')
                GROUP BY ad_id,  gender, age

                UNION

                SELECT ad_id, CASE WHEN gender = 'man' THEN 'all'
                    ELSE 'all' 
                    END as gender, age ,count(*) as cnt
                FROM target
                WHERE ad_id in 
                (SELECT ad_id FROM advert WHERE user_id=%s)
                and age in ('kids', 'silver')
                GROUP BY ad_id,  age
                ORDER BY ad_id, gender, age;'''

        # 접속한 아이디가 등록한 광고의 CPM
        sql_cpm = '''SELECT sub.ad_name, ROUND(sub.cost/sub.cnt*1000,2) as CPM
                FROM (SELECT ad.ad_name, ad.ad_id, ad.budget/ad.period as cost, count(t.ad_id) as cnt
                FROM advert ad LEFT JOIN target t ON ad.ad_id = t.ad_id
                GROUP BY ad.ad_id, t.ad_id) sub
                WHERE sub.ad_name in 
                    (SELECT ad_name
                    FROM advert
                    WHERE user_id=%s)
                GROUP BY sub.ad_name;'''

        sql_cnt = '''SELECT ad_id,COUNT(ad_id) AS cnt
                FROM target
                WHERE ad_id IN 
                (SELECT ad_id FROM advert WHERE user_id=%s)
                GROUP BY ad_id;'''
    

        try:
            conn = pymysql.connect(**Config.config)
            cur = conn.cursor()
            
            cur.execute(sql_gender, [user_id])
            gender_cnt = cur.fetchall()

            cur.execute(sql_age, [user_id])
            age_cnt = cur.fetchall()

            cur.execute(sql_target, [user_id, user_id])
            target_cnt = cur.fetchall()

            cur.execute(sql_cpm, [user_id])
            cpm = cur.fetchone()

            cur.execute(sql_cnt, [user_id])
            cnt = cur.fetchone()

        except pymysql.IntegrityError:

            return Response(dumps({"message": "로딩할 수 없습니다.."}), status=200, mimetype='application/json')

        if len(gender_cnt) > 0 and len(age_cnt) > 0 and len(target_cnt) > 0 and len(cpm) > 0:
            response_data = {
                 "ad_name" : gender_cnt[0][0], "ad_id" : target_cnt[0][0],
                 "man" : gender_cnt[0][2], "woman" : gender_cnt[1][2],
                 "cpm" : cpm[1], "cnt" : cnt[1],
            }

            if user_id == 4:
                response_data.update({"reach" : 64.55})
                response_data.update({"frequency" : 1.25})

            else:
                response_data.update({"reach": 84.46})
                response_data.update({"frequency" : 1.42})

            for i in range(len(age_cnt)):
                response_data.update({"age_" + age_cnt[i][1] : age_cnt[i][2]})
            
            for i in range(len(target_cnt)):
                if target_cnt[i][2] == 'kids':
                    response_data.update({"kids" : target_cnt[i][3]})
                
                elif target_cnt[i][2] == 'silver':
                    response_data.update({"silver" : target_cnt[i][3]})
                
                elif target_cnt[i][1] == 'man' and target_cnt[i][2] == '2030':
                    response_data.update({"age_2030m" : target_cnt[i][3]})

                elif target_cnt[i][1] == 'woman' and target_cnt[i][2] == '2030':
                    response_data.update({"age_2030w" : target_cnt[i][3]})

                elif target_cnt[i][1] == 'man' and target_cnt[i][2] == '4050':
                    response_data.update({"age_4050m" : target_cnt[i][3]})

                elif target_cnt[i][1] == 'woman' and target_cnt[i][2] == '4050':
                    response_data.update({"age_4050w" : target_cnt[i][3]})
            
            return response_data, 201
        
        else:
            response_data = dict()

            return response_data, 200


class Admin(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()['user_id']
        
        # 광고 CPM
        sql_cpm = '''SELECT sub.ad_name, ROUND(sub.cost/sub.cnt*1000,2) as CPM
                FROM (SELECT ad.ad_name, ad.ad_id, ad.budget/ad.period as cost, count(t.ad_id) as cnt
                FROM advert ad LEFT JOIN target t ON ad.ad_id = t.ad_id
                GROUP BY ad.ad_id, t.ad_id) sub
                GROUP BY sub.ad_name;'''

        # 회사별 수익
        sql_revenue = '''SELECT user.company_name, a.user_id, sum(a.budget) as "revenue" 
                    FROM advert a LEFT JOIN users user ON a.user_id = user.user_id
                    GROUP BY a.user_id;'''

        # 월별 총 수익
        sql_month = '''SELECT SUM(rev.cost) as revenue
                FROM (SELECT ad_id, MONTH(now()) - MONTH(created_at) AS Month, budget/period AS cost, period 
                FROM advert) rev 
                WHERE  rev.Month < rev.period;'''

        # 전체 등록된 광고 수(현재 시점)
        sql_cnt = '''SELECT count(sub.ad_id) AS "advert cnt"
                FROM (SELECT ad_id, MONTH(now()) - MONTH(created_at) AS Month, period
                FROM advert)sub
                WHERE sub.Month < sub.period;'''

        try:
            conn = pymysql.connect(**Config.config)
            cur = conn.cursor()
            
            cur.execute(sql_cpm)
            cpm = cur.fetchall()

            cur.execute(sql_revenue)
            revenue = cur.fetchall()

            cur.execute(sql_month)
            month = cur.fetchone()

            cur.execute(sql_cnt)
            cnt = cur.fetchone()

        except pymysql.IntegrityError:

            return Response(dumps({"message": "등록 할수 없습니다."}), status=200, mimetype='application/json')

        response_data ={}
        if len(cpm) > 0 and len(revenue) > 0 and len(month) > 0 and len(cnt) > 0:
            response_data = {
                "cnt" : cnt[0], "month" : month[0], "cpm" : {cpm[0][0] : cpm[0][1]},
                "revenue" : {revenue[0][0] : revenue[0][2]},
            }

            for i in range(1, len(cpm)):
                response_data["cpm"].update({cpm[i][0] : cpm[i][1]})

            for i in range(1, len(revenue)):
                response_data["revenue"].update({revenue[i][0] : revenue[i][2]})

        return response_data, 201


api.add_resource(Mypage, '/mypage')
api.add_resource(Admin, '/admin')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)