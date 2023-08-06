from flask import Flask
import os

import aws_operations
import threading, time
import math
import requests

ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_2/manager_app/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

FRONTEND_LOCATION = 'https://4e2pagon46.execute-api.us-east-1.amazonaws.com/dev'
AUTO_SCALER_LOCATION = 'https://xywel9r260.execute-api.us-east-1.amazonaws.com/dev'
MANAGER_APP_LOCATION = 'https://15y2gmsoyb.execute-api.us-east-1.amazonaws.com/dev'
LAMBDA_LOCATION_API = 'https://i3aj0vxx06.execute-api.us-east-1.amazonaws.com/user'
LAMBDA_BACKUP_API = 'https://9wcsyh8j45.execute-api.us-east-1.amazonaws.com/db'


global memcache_ec2

memcache_ec2 = {
    'memcache0': None,
    'memcache1': None,
    'memcache2': None,
    'memcache3': None,
    'memcache4': None,
    'memcache5': None,
    'memcache6': None,
    'memcache7': None,
}

def update_auto_scaler():
    while True:
        if auto_scaler.config['mode'] == 0:
            running_ipv4_dict = aws_operations.get_ec2_ip4_addresses(region='us-east-1')

            metric_dict = {}
            curr_node_count = len(running_ipv4_dict.keys())

            for i in range(curr_node_count):
                metric_dict[str(i)] = aws_operations.get_cloudwatch_stats(instance_id=i)

            miss_rate = []

            for _, metric in metric_dict.items():
                if len(metric['no_request']['Datapoints']) != 0:
                    total_request = metric['no_request']['Datapoints'][0]['Sum']
                    total_miss = metric['miss_rate']['Datapoints'][0]['Sum']
                    miss_rate.append(total_miss/total_request if total_request != 0 else 0)
                # total_hit += metric['hit_rate']['Datapoints'][0]['Average']

    # auto_scaler.config['Max_Miss_Rate_threshold'] = 0.7
    # auto_scaler.config['Min_Miss_Rate_threshold'] = 0.3
    # auto_scaler.config['Ratio_by_which_to_expand_the_pool'] = 2.0
    # auto_scaler.config['Ratio_by_which_to_shrink_the_pool'] = 0.5
            

            ratio = sum(miss_rate) / len(miss_rate) if len(miss_rate) != 0 else 0
            print(miss_rate, ratio)

            if ratio > float(auto_scaler.config['Max_Miss_Rate_threshold']) and len(miss_rate) != 0:
                new_node_count = math.ceil(float(auto_scaler.config['Ratio_by_which_to_expand_the_pool']) * curr_node_count)
                
                if new_node_count > 8:
                    new_node_count = 8
                
                if new_node_count != curr_node_count:
                    print("Scale UP")
                    print(curr_node_count, new_node_count)


                    all_keys = requests.post(str(FRONTEND_LOCATION + 'retrieve_all_keys'))
                    user_id = requests.post(str(FRONTEND_LOCATION) + 'get_user_id')

                    aws_operations.start_memcache_ec2(curr_node_count, new_node_count-1)

                    requests.post(str(MANAGER_APP_LOCATION + 'configure_memcache_external'), params={'size': new_node_count})

                    requests.post(str(MANAGER_APP_LOCATION + 'rebalance_keys'), params={'keys': all_keys.json(), 'size': new_node_count, 'user_id': user_id})

            elif ratio < float(auto_scaler.config['Min_Miss_Rate_threshold']) and len(miss_rate) != 0:
                new_node_count = math.ceil(float(auto_scaler.config['Ratio_by_which_to_shrink_the_pool']) * curr_node_count)
                
                if new_node_count < 1:
                    new_node_count = 1

                if new_node_count != curr_node_count:
                    print("Scale DOWN")
                    print(curr_node_count, new_node_count)
                    

                    all_keys = requests.post(str(FRONTEND_LOCATION + 'retrieve_all_keys'))
                    user_id = requests.post(str(FRONTEND_LOCATION) + 'get_user_id')

                    
                    aws_operations.stop_memcache_ec2(new_node_count, curr_node_count-1)

                    requests.post(str(MANAGER_APP_LOCATION + 'rebalance_keys'), params={'keys': all_keys.json(), 'size': new_node_count, 'user_id': user_id})



    
        time.sleep(600)

threading.Thread(target=update_auto_scaler, daemon=True).start()



auto_scaler = Flask(__name__)
auto_scaler.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auto_scaler.config['IMAGE_FOLDER'] = IMAGE_FOLDER

auto_scaler.config['Max_Miss_Rate_threshold'] = 0.7
auto_scaler.config['Min_Miss_Rate_threshold'] = 0.3
auto_scaler.config['Ratio_by_which_to_expand_the_pool'] = 2.0
auto_scaler.config['Ratio_by_which_to_shrink_the_pool'] = 0.5
auto_scaler.config['mode'] = 0
# auto_scaler.config['mode'] = 1



from app import main
