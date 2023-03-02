import os
import json
import requests
from time import gmtime, strftime
from screenshot import ScreenshotTDV
from flask import Flask, request

with open("config.json", "r") as config:
    data = json.load(config)
    # Line notify access token
    ACCESS_TOKEN = data['access_token']
    # TDV username, password
    username = data['username']
    password = data['password']

app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print('-'*30)
        print(current_time)
        req = request.json
        message = req['message']
        chart_detail = message.split('\n')[1]
        strategies = message.split('\n')[2]

        exchange = chart_detail.split('-')[0]
        symbol = chart_detail.split('-')[1]
        interval = chart_detail.split('-')[2]
        template = strategies

        # Capture currently screen function
        tdv = ScreenshotTDV(
                        username=username, password=password, 
                        exchange=exchange, symbol=symbol, 
                        interval=interval, template=template

        )
        tdv.main()
        
        # # Notify message & image function
        notify_message(message)
        return req, 200

    elif request.method == 'GET':
        return 'Webhook', 200

# text & image reply message    
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
        # print(r.status_code)
        # print(r.text)

if __name__ == '__main__':

    app.run(debug=True, port=5000)


