import os
import requests
from screenshot import tradingview_screenshot
from flask import Flask, request

# Line notify access token
ACCESS_TOKEN = 'Bearer uqt8a2SlZ0mOLS1pR2xIUvs490eaxxLH9XY9fcXJOpj'
username = 'test.eaforex@gmail.com'
password = '123456789zz**'


app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        req = request.json
        message = req['message']
        symbol = message.split(' ')[1]
        # Capture currently screen
        tradingview_screenshot(username=username, password=password, symbol=symbol)
        # notify message & image
        notify_message(message)
        return req, 200

    elif request.method == 'GET':
        return 'Webhook', 200

# text&image reply message    
def notify_message(message):
    file_name = 'screenshot.png'
    path = os.path.dirname(os.path.realpath(__file__))
    path_img = r"{}\{}".format(path, file_name)

    with open(path_img, 'rb') as f:
        files = {'imageFile':(file_name, f, 'image/png')}
        url = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization':ACCESS_TOKEN} #'Content-Type':'multipart/form-data',
        payload = {'message':message}  
        r = requests.post(url, headers=headers, params=payload, files=files)
        print(r.status_code)
        print(r.text)

if __name__ == '__main__':

    app.run(debug=True, port=8000)