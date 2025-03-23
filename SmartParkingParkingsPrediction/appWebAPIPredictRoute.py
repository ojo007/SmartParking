from flask import Flask
from flask import request
from flask import Response
import nmap
import json
import os
import queue
from werkzeug.exceptions import BadRequestKeyError
import ipaddress
#from waitress import serve
from gevent.pywsgi import WSGIServer
from flask_httpauth import HTTPBasicAuth
from DNN import DNN
from LSTM import DNN_LSTM
from FBNN import FBNN


appWebAPIPredictRoute = Flask(__name__)
appWebAPIPredictRoute.debug = True
auth = HTTPBasicAuth()
Queue=queue.Queue()
ResultsDictionary={}

# gmp = None

@auth.verify_password
def verify_password(username, password):
    if not username=="agent" and not password=="executor":
        return False
    return True


def predictBasedOnInput(input_features,DNN_to_run,models2Features,models6Features):
    if (len(input_features)==6):
        return models6Features[DNN_to_run].predictsSetupExecute(input_features,6)
    else:    
        return models2Features[DNN_to_run].predictsSetupExecute(input_features,2)

@appWebAPIPredictRoute.route('/predict', methods=['POST'])
@auth.login_required
def predictNextRouter():
    try:
        gnp = nmap.PortScanner()
        jsonReq = request.get_json(force=True)
        input_features =  json.loads(jsonReq["input_features"])
        DNN_to_run = json.loads(jsonReq["DNN_to_run","FBNN"])        
    except BadRequestKeyError as ex: 
      print('Unknown key: "{}"'.format(ex.args[0]))  
      return 'Unknown key: "{}"'.format(ex.args[0]), 500  
    print("The input_features")
    print(input_features)
    print("Type of deserialized data: ", type(input_features))
    print("The DNN_to_run")
    print(DNN_to_run)    
    predicted_result=predictBasedOnInput(input_features,DNN_to_run,models2Features,models6Features)   
    return Response(json.dumps(str(predicted_result)))



@appWebAPIPredictRoute.route('/predict', methods=['GET'])
@auth.login_required
def predictNextRouterGET():
    try:
      args = request.args
      input_features = json.loads(args.get('input_features'))
      DNN_to_run = args.get('DNN_to_run') 
      target_scanner_id =  args.get("scanner_id")
      scanner =  args.get("scanner")
      if (DNN_to_run==None):
          DNN_to_run="nmap"
      print("The input_features")
      print(input_features)
      print("Type of deserialized data: ", type(input_features))      
      print("The DNN_to_run")
      print(DNN_to_run)  
    except BadRequestKeyError as ex: 
      print('Unknown key: "{}"'.format(ex.args[0]))  
      return 'Unknown key: "{}"'.format(ex.args[0]), 500  
    predicted_result=predictBasedOnInput(input_features,DNN_to_run,models2Features,models6Features)   
    return Response(json.dumps(str(predicted_result)))




if __name__ == '__main__':
    print("Models Setup and Test")
    csv_file = 'parking_details.csv'
    data = "DNN"
    dNN2 = DNN(data, csv_file,2)    
    dNN6 = DNN(data, csv_file,6)
    data = "DNN_LSTM"
    dnn_LSTM2 = DNN_LSTM(data, csv_file,2)    
    dnn_LSTM6 = DNN_LSTM(data, csv_file,6)
    data = "FBNN"    
    fbNN2 = FBNN(data, csv_file,2)    
    fbNN6 = FBNN(data, csv_file,6)    
    models2Features={"DNN":dNN2,"DNN_LSTM":dnn_LSTM2,"FBNN":fbNN2}
    models6Features={"DNN":dNN6,"DNN_LSTM":dnn_LSTM6,"FBNN":fbNN6}  
    print("Starting the Server..")
    appWebAPIPredictRoute.config["SECRET_KEY"] = "ITSASECRET"
    http_server = WSGIServer(('0.0.0.0', 5000), appWebAPIPredictRoute, keyfile='server.key', certfile='server.crt')
    http_server.serve_forever()
