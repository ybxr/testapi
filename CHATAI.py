import re
import time
import hashlib
import requests
import datetime
import sqlite3




class ChatAi:
    
    def __init__(self):
        self.Authorization = None
        
    @staticmethod
    def md5(s):
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def update(self):
        data = list(SqlMsg.get_session()[0])
        email = data[1]
        password = data[2]
        session = self.login(email, password)
        data[4] = session
        SqlMsg.update_session(data)
        self.Authorization = session

    def get_massage(self,questions):
        self.update()
        url = "https://wetabchat.haohuola.com/api/chat/conversation"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Authorization": "Bearer "+self.Authorization,
            "Connection": "keep-alive",
            "Content-Length": "19",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "wetabchat.haohuola.com",
            "i-app": "hitab",
            "i-branch": "zh",
            "i-lang": "zh-CN",
            "i-platform": "edge",
            "i-version": "1.0.39",
            "Origin": "chrome-extension://bpelnogcookhocnaokfpoeinibimbeff",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
        }
        data = {
                "prompt": questions,
                "conversationId": "",
                "assistantId": "",
                "model": "650e52e9c4bcb4a52791b599"
            }
        # res = requests.post(url, headers=headers, json=data)
        # print(res.text)
        # result = r"".join(re.findall('{"data":"(.*?)","code":0,"message":"成功"}',res.text))
        # result = result.replace("WeTab新标签页","一个").replace("\\n","\n")
        return {"url":url, "headers":headers, "json":data}

    def login(self,username, password):
        url = "https://api.wetab.link/api/user/login"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.wetab.link",
            "i-app": "hitab",
            "i-branch": "zh",
            "i-lang": "zh-CN",
            "i-platform": "edge",
            "i-version": "1.0.39",
            "Origin": "chrome-extension://bpelnogcookhocnaokfpoeinibimbeff",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
        }
        data = {
            "email": username,
            "password": ChatAi.md5(password)
            }
        res = requests.post(url, headers=headers, json=data)
        data = res.json()
        # print(data)
        # code = data["code"]
        # message = data["message"]
        # user_id = data["data"]["user"]["id"]
        # nickname = data["data"]["user"]["nickname"]
        # email = data["data"]["user"]["email"]
        token = data["data"]["token"]
        # refreshToken = data["data"]["refreshToken"]
        self.Authorization = token
        return token

class SqlMsg:

    @staticmethod
    def get_now_date():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")
        
    @staticmethod
    def sqlexec(sql):
        dbName = "Secretkey.sqlite"
        db = sqlite3.connect(dbName)
        cur = db.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        db.commit()
        cur.close()
        db.close()
        return  result
        
    @staticmethod
    def get_session():
        sql = """
            SELECT
                * 
            FROM
                pwd
            WHERE
                (lasttime = '%s' AND count <3) OR lasttime < '%s' OR count IS NULL
            LIMIT 1;
            """%(SqlMsg.get_now_date(),SqlMsg.get_now_date())
        return SqlMsg.sqlexec(sql)
    
    @staticmethod
    def update_session(sql_result):
        id = sql_result[0]
        session = sql_result[4] or ""
        lasttime = SqlMsg.get_now_date()
        count = sql_result[6] or 0
        if count >=3 :
            count = 0
        count += 1
        sql = """
            UPDATE 
                pwd
            SET 
                session = '{0}',
                count = {1},
                lasttime = '{2}'
            WHERE
                id = {3};
            """.format(session,count,lasttime,id)
        # print(sql)
        return SqlMsg.sqlexec(sql)


if __name__ == "__main__":
    cai = ChatAi()
