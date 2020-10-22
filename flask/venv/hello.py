
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def yourMethod():
    if request.method == 'POST':
        print(request.data)
        response = jsonify({'fuck':'you'})
    else:
        response = 'haha'
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response