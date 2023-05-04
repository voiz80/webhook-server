from flask import Flask, request, abort, Response, jsonify
import logging
import pymongo
import json
import hashlib, hmac
from bson.objectid import ObjectId
import base64
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv() 

### Logger for Gunicorn and mount file on the host: webhook_log.log ###
logging.basicConfig(filename='webhook_log.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Load 4 Worker ...')

#SECRET = 'Unl00cezp105!'

### Verification Post connection ### 
def verifySignature():
    signature = hmac.new(bytes(os.getenv("SECRET").encode('ascii')), str(request.json['data']).encode('ascii'), digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, request.json['chk'])

### Mongo connect ###
try:
    client = pymongo.MongoClient(
        host = 'test_mongodb',
        port = 27017,
        username = 'root',
        password = os.getenv("DB_PASSWORD"),
        authSource = 'admin',
        serverSelectionTimeoutMS = 1000
    )

    dbtable = client["office"]
    offices = dbtable["offices"]
    workstation = dbtable["workstation"]

    client.server_info() # trigger exception if cannot connect db
except:
    print("ERROR - Cannot connect to db")
    app.logger.info(f'ERROR - Cannot connect to db: {request.remote_addr}')

### Routing ###
@app.route('/', methods=['Get'])
def index_test():
    app.logger.info(f'GET/ {request.remote_addr}')
    try:
        return Response(
            response= json.dumps({"message": "EasyWebhook | Page/Route only for TEST ...", "/showoffices": "show all insert data", "/webhook": "Accept POST and insert in mongodb"}),
            status=200,
            mimetype="application/json"
        )

    except Exception as ex:
        print(ex)
    
@app.route('/showoffices', methods=['Get'])
def index_show_offices():
    app.logger.info(f'GET/showoffices {request.remote_addr}')
    try:
        
        data = list(offices.find())
        for id in data:
            id["_id"] = str(id["_id"])
        return Response(
        response= json.dumps(data, ensure_ascii=False).encode("utf8"),
        status=200,
        mimetype="application/json"
        )

    except Exception as ex:
        print(ex)

### Accept ... ###
@app.route('/webhook', methods=['POST'])
def webhook_test():
    try:
        data = request.get_json()
        app.logger.info(f'/POST from {request.remote_addr} with hostname: {data.keys()}')

        ### If not Verifity hmac ###
        if not data or verifySignature:
            app.logger.info(f'Signature Verification Failed from {request.remote_addr} with hostname: {data.keys()}')
            return jsonify({"error": "No data provided || Signature Verification Failed"}), 400
        
        ### Insert the data into MongoDB ###
        res_id = workstation.insert_one(data)
        app.logger.info(f'Webhook received! from {request.remote_addr} and inserted with id: {res_id.inserted_id} with hostname: {data.keys()}')
        return jsonify({"message": "Data inserted successfully", "id": {res_id.inserted_id}})

    except json.JSONDecodeError:
        app.logger.error(f'ERORR 400! from {request.remote_addr} with hostname: {data.keys()}')
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        app.logger.error(f'ERORR 500! from {request.remote_addr} with hostname: {data.keys()}')
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
