
from flask import Flask, jsonify, request
from VaunixDevices import VaunixDevices

app = Flask(__name__)
deviceManagers = {
    'VaunixDevices': VaunixDevices(),
}

def getAllDevicesData():
    allDevicesData = {}
    for key, manager in deviceManagers.items():
        allDevicesData[key] = manager.devicesData
    return allDevicesData

@app.route('/', methods=['GET', 'POST'])
def yourMethod():
    if request.method == 'GET':
        response = jsonify(getAllDevicesData())
    if request.method == 'POST':
        req = request.get_json(force=True)
        status, result = deviceManagers[req['managerId']].handleRequest(req['type'], req['args'])
        response = jsonify({ 'status':status, 'result':result })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response