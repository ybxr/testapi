import requests
import asyncio
import websockets
import re
import re
import time
import hashlib
import requests
import random
import ddddocr
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM



class yzm:
    @staticmethod
    def svg_iamge(svg_file, image_file):
        drawing = svg2rlg(svg_file)
        renderPM.drawToFile(drawing, image_file, fmt='PNG')
    @staticmethod
    def image_txt():
        ocr = ddddocr.DdddOcr(old=True, show_ad=False)
        with open('yzm.png', 'rb') as f:
            img_bytes = f.read()
        res = ocr.classification(img_bytes)
        return res
    @staticmethod
    def shibie():
        yzm.svg_iamge("yzm.svg", 'yzm.png')
        data = yzm.image_txt()
        print(data)
        return data
def get_password():
    s = "abcdefghijklmnopqrstuvwxyz0123456789"
    pwd = ""
    for i in range(15):
        pwd += random.choice(s)
    e_pwd = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    return pwd,e_pwd

def register(email):
    yzm_url = "https://api.wetab.link/api/verify/image?i-branch=zh&type=register&t="+str(time.time()*1000)
    headers = {
        "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Host": "api.wetab.link",
        "i-app": "hitab",
        "i-branch": "zh",
        "i-lang": "zh-CN",
        "i-platform": "edge",
        "i-version": "1.0.39",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
    }
    res = requests.get(yzm_url, headers=headers)
    with open("yzm.svg","w") as f:
        f.write(res.text)
    Cookie = res.headers["Set-Cookie"].split(";")[0]
    send_url = "https://api.wetab.link/api/verify/send-email"
    data = {"email": email, "type": "register", "imgCode": yzm.shibie()}
    headers["Cookie"] = Cookie
    res = requests.post(send_url, headers=headers, json=data)
    print("开始识别：",res.json()['message'])
    return res.json()['message']
    # if res.json()['message'] == "success":
    # {"code":4011,"message":"邮箱验证码错误","timestamp":1685413778534,"data":null}
def verify(email,emailCode,password):
    verify_url = "https://api.wetab.link/api/verify/verify-email"
    data = {"email": email, "type": "register", "emailCode": emailCode}
    headers = {
        "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Host": "api.wetab.link",
        "i-app": "hitab",
        "i-branch": "zh",
        "i-lang": "zh-CN",
        "i-platform": "edge",
        "i-version": "1.0.39",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
    }
    res = requests.post(verify_url, headers=headers, json=data)
    print("开始核对验证码：",res.json()["message"])
    registerurl = "https://api.wetab.link/api/user/register"
    data = {"email": email, 
            "password": password, 
            "emailCode": emailCode,
            "nickname":email,
            "password": password
    }
    res = requests.post(registerurl, headers=headers, json=data)
    print("注册事件：",res.json()["message"])


def get_email_code(data):
    yzm = re.findall(r'<p><b>(\d{6})</b></p>',data)[0]
    return yzm 
def get_email(data):
    email = re.findall(r'\["shortid","(.+?)"\]',data)[0]
    return email 
def get_cookie():
    url = "https://world-mail.ml/socket.io/?EIO=3&transport=polling&t=1685436550830-0"
    headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    res = requests.get(url,headers=headers)
    sid = res.headers["Set-Cookie"].split(";")[0].replace("io=","")
    remote = "wss://world-mail.ml/socket.io/?EIO=3&transport=websocket&sid="+sid
    return remote
async def hello():
    async with websockets.connect(remote) as websocket:
        await websocket.send('2probe')
        greeting = await websocket.recv()
        print(f"> {greeting}")
        await websocket.send('5')
        greeting = await websocket.recv()
        print(f"> {greeting}")
        while True:
            await websocket.send('2')
            greeting = await websocket.recv()
            print(f"> {greeting}")
            await websocket.send('42["request shortid",true]')
            data = await websocket.recv()
            email = get_email(data)+"@world-mail.ml"
            print(f"> {email}")
            if email[0] in "abcdefghijklmnopqrstuvwxyz":
                # 开始注册事件
                data = register(email)
                if data != "success":
                    time.sleep(2)
                    continue
                else:
                    time.sleep(3)
                data = await websocket.recv()
                emailCode = get_email_code(data)
                password,e_pwd = get_password()
                verify(email,emailCode,e_pwd)
                with open("Secretkey.csv", "a") as f:
                    f.write(f"{email},{password},{e_pwd}\n")
            time.sleep(3)
            
            
remote = get_cookie()
asyncio.get_event_loop().run_until_complete(hello())


