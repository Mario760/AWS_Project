from ctypes import sizeof
from flask import render_template, url_for, request
# import db_operations
from app import webapp, memcache_ec2
from flask import json
import os, requests
import base64, sys
import aws_operations
import boto3
import request_routing
import time

"'http://100.67.9.114:5001/'"
"'http://127.0.0.1:5001/'"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

FRONTEND_LOCATION = 'https://4e2pagon46.execute-api.us-east-1.amazonaws.com/dev/'
AUTO_SCALER_LOCATION = 'https://xywel9r260.execute-api.us-east-1.amazonaws.com/dev/'
MANAGER_APP_LOCATION = 'https://15y2gmsoyb.execute-api.us-east-1.amazonaws.com/dev/'
LAMBDA_LOCATION_API = 'https://i3aj0vxx06.execute-api.us-east-1.amazonaws.com/user'
LAMBDA_BACKUP_API = 'https://9wcsyh8j45.execute-api.us-east-1.amazonaws.com/db'





DEFAULT_CAPACITY = 1000
DEFAULT_POLICY = 'RR'

total_stat = {'no_items': 0,
              'total_size': 0,
              'no_request': 0,
              'miss_rate': 0,
              'hit_rate': 0
              }


s3_bucket = aws_operations.Bucket('ece1779-project2-bucket0', 'us-east-1')

def check_img_name(filename: str) -> bool:
    """
    Check if file is an acceptable image.

    >>> check_image("XXX.jpg")
    True
    >>> check_image("XXX.pdf")
    False
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@webapp.route('/')
def main():
    return render_template("main.html")


@webapp.route('/clear_memcache')
def clear_memcache():
    return render_template("clear_memcache.html")

@webapp.route('/config_memcache')
def config_memcache():
    return render_template("config_memcache.html")

@webapp.route('/get_memcache_stats')
def get_memcache_stat():
    return render_template("get_memcache_stats.html")

@webapp.route('/resize_pool')
def resize_pool():
    return render_template("resize_pool.html")

@webapp.route('/delete_all_data')
def delete_all_data():
    return render_template("delete_all_data.html")

@webapp.route('/backup')
def backup():
    return render_template("backup.html")

@webapp.route('/display_memcache_keys')
def display_memcache_key():
    return render_template("display_memcache_keys.html")

@webapp.route('/backup_db', methods=['POST'])
def backup_db():
    url = LAMBDA_BACKUP_API + "/table"
    body = {
        "table_name": "user_auth"
    }
    payload = json.dumps(body)
    response_0 = requests.post(url, data=payload)
    body = {
        "table_name": "user_info"
    }
    payload = json.dumps(body)
    response_1 = requests.post(url, data=payload)

    res_dict = {}
    res_dict['user_auth'] = response_0.json()
    res_dict['user_info'] = response_1.json()

    return json.dumps(res_dict)

@webapp.route('/resize_pool_function',methods=['POST'])
def resize_pool_function():
    method = request.form.get('resize_method')
    curr_pool = len(list(aws_operations.get_ec2_ip4_addresses().values()))

    if method == "manual":
        return render_template("manual_resize_pool.html", pool_count=curr_pool)
    elif method == "automatic":
        return render_template("auto_resize_pool.html", pool_count=curr_pool)

@webapp.route('/auto_resize_pool',methods=['POST'])
def auto_resize_pool():
    requests.post(str(AUTO_SCALER_LOCATION + 'config_manual_auto'), params={'mode': 'auto'})

    Max_Miss_Rate_threshold = request.form.get('Max_Miss_Rate_threshold')
    Min_Miss_Rate_threshold = request.form.get('Min_Miss_Rate_threshold')
    Ratio_by_which_to_expand_the_pool = request.form.get('Ratio_by_which_to_expand_the_pool')
    Ratio_by_which_to_shrink_the_pool = request.form.get('Ratio_by_which_to_shrink_the_pool')
    
    params = {
        'Max_Miss_Rate_threshold': str(Max_Miss_Rate_threshold),
        'Min_Miss_Rate_threshold': str(Min_Miss_Rate_threshold),
        'Ratio_by_which_to_expand_the_pool': str(Ratio_by_which_to_expand_the_pool),
        'Ratio_by_which_to_shrink_the_pool': str(Ratio_by_which_to_shrink_the_pool),
    }

    config_res = requests.post(str(AUTO_SCALER_LOCATION + 'config_auto_scaler'), params=params)
    return "OK"



@webapp.route('/manual_resize_pool',methods=['POST'])
def manual_resize_pool():
    requests.post(str(AUTO_SCALER_LOCATION + 'config_manual_auto'), params={'mode': 'manual'})

    curr_pool = len(list(aws_operations.get_ec2_ip4_addresses().values()))
    pool_count = int(request.form.get('pool_count'))
    if pool_count > 8:
        return "Pool Count too large!"
    elif pool_count < 1:
        return "Pool Count too small!"
    
    all_keys = requests.post(str(FRONTEND_LOCATION + 'retrieve_all_keys'))
    # keys = []
    # for i in range(len(all_keys.json())):
    #     keys.append(all_keys.json()[i][0])
    print(all_keys.json())

    if curr_pool < pool_count:
        aws_operations.start_memcache_ec2(curr_pool, pool_count-1)
        configure_memcache_internal(pool_count)
        
    elif curr_pool > pool_count:
        aws_operations.stop_memcache_ec2(pool_count, curr_pool-1)


    requests.post(str(MANAGER_APP_LOCATION + 'rebalance_keys'), params={'keys': all_keys.json(), 'size': pool_count})
        
    return "Resized pool size to {0} nodes.".format(pool_count)

@webapp.route('/clear',methods=['POST'])
def clear():
    # """
    # Drop all keys in memcache.
    # """
    # memcache_loc = list(aws_operations.get_ec2_ip4_addresses().values())
    # for memcache in memcache_loc:
    #     clear_res = requests.post(str('http://' + memcache + ':5001/' + 'clear'))

    # # clear_res = requests.post(str(MEMCACHE_LOCATION + 'clear'))

    # if clear_res.status_code != 200:
    #     return clear_res

    # requests.post(FRONTEND_LOCATION + 'clear_local_keys')

    clear_res = requests.post(FRONTEND_LOCATION + 'clear')

    return "OK"



@webapp.route('/clear_2',methods=['POST'])
def clear_2():
    """
    Drop all keys in memcache.
    """
    memcache_loc = list(aws_operations.get_ec2_ip4_addresses().values())
    for memcache in memcache_loc:
        clear_res = requests.post(str('http://' + memcache + ':5001/' + 'clear'))

    # clear_res = requests.post(str(MEMCACHE_LOCATION + 'clear'))

    if clear_res.status_code != 200:
        return clear_res

    return clear_res.json()


@webapp.route('/delete',methods=['POST'])
def delete():
    """
    Delete all application data
    """
    s3_bucket.delete_all_images()
    # db_operations.delete_all_pairs()
    url = LAMBDA_LOCATION_API + "/images"
    requests.delete(url)



    clear_res = requests.post(FRONTEND_LOCATION + 'clear')


    return "Successfully deleted all data"



@webapp.route('/configure_memcache_external', methods=['POST'])
def configure_memcache_external():
    """
    Configure Memcache, including Memcache capacity and Replacement Policy.
    Default Capacity: 10MB. Default Policy: Random Replacement
    """
    # capacity = request.form.get('capacity')
    # policy = request.form.get('rep_policy')
    
    size = request.args.get('size')

    capacity = webapp.config['CAPACITY']
    policy = webapp.config['POLICY']


    if int(capacity) > 1000:
        return "Capacity Too big! Must be smaller than 1000 MB"
    if int(capacity) < 0:
        return "Capacity Too small! Must be at least 0MB"
    if str(policy) != 'RR' and str(policy) != 'LRU':
        return policy

    # db_operations.put_memcache_config(int(capacity), policy)
    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    while (len(running_ipv4_dict.keys()) != int(size)):
        time.sleep(1)
        running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()

    def retry(url, params):
        try:
            return requests.post(url + 'config_memcache', params=params)
        except Exception:
            time.sleep(1)
            return retry(url, params)

    for i, ipv4 in running_ipv4_dict.items():
        memcache_loc = 'http://' + str(ipv4) + ':5001/'
        params = {'capacity': str(capacity), 'policy': str(policy)}
        res = retry(memcache_loc, params)
        # print(str('http://' + memcache + ':5001/' + 'config_memcache'))

    return "OK"



@webapp.route('/configure_memcache_internal', methods=['POST'])
def configure_memcache_internal(size: int):
    """
    Configure Memcache, including Memcache capacity and Replacement Policy.
    Default Capacity: 10MB. Default Policy: Random Replacement
    """
    # capacity = request.form.get('capacity')
    # policy = request.form.get('rep_policy')
    
    capacity = webapp.config['CAPACITY']
    policy = webapp.config['POLICY']

    if int(capacity) > 1000:
        return "Capacity Too big! Must be smaller than 1000 MB"
    if int(capacity) < 0:
        return "Capacity Too small! Must be at least 0MB"
    if str(policy) != 'RR' and str(policy) != 'LRU':
        return policy

    # db_operations.put_memcache_config(int(capacity), policy)
    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    while (len(running_ipv4_dict.keys()) != int(size)):
        time.sleep(1)
        running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()

    def retry(url, params):
        try:
            return requests.post(url + 'config_memcache', params=params)
        except Exception:
            time.sleep(1)
            return retry(url, params)

    for i, ipv4 in running_ipv4_dict.items():
        memcache_loc = 'http://' + str(ipv4) + ':5001/'
        params = {'capacity': str(capacity), 'policy': str(policy)}
        res = retry(memcache_loc, params)
        # print(str('http://' + memcache + ':5001/' + 'config_memcache'))

    return "OK"

@webapp.route('/configure_memcache', methods=['POST'])
def configure_memcache():
    """
    Configure Memcache, including Memcache capacity and Replacement Policy.
    Default Capacity: 10MB. Default Policy: Random Replacement
    """
    capacity = request.form.get('capacity')
    policy = request.form.get('rep_policy')
    webapp.config['CAPACITY'] = capacity
    webapp.config['POLICY'] = policy
    
    if not capacity.isdigit():
        return "Enter a Vaild Capacity"
    if int(capacity) > 1000:
        return "Capacity Too big! Must be smaller than 1000 MB"
    if int(capacity) < 0:
        return "Capacity Too small! Must be at least 0MB"
    if str(policy) != 'RR' and str(policy) != 'LRU':
        return policy

    # db_operations.put_memcache_config(int(capacity), policy)
    memcache_loc = list(aws_operations.get_ec2_ip4_addresses().values())
    for memcache in memcache_loc:
        print(memcache)
        config_res = requests.post(str('http://' + memcache + ':5001/' + 'config_memcache'), params={'capacity': str(capacity), 'policy': str(policy)})
        # print(str('http://' + memcache + ':5001/' + 'config_memcache'))

    return config_res.json()

# @webapp.route('/get_memcache_stats', methods=['POST'])
# def get_memcache_stats():
#     """
#     Display MemCache Statistics over past 10 minutes.
#     """
    
#     memcache_stats = db_operations.get_memcache_stat()

#     return memcache_stats

@webapp.route('/charts', methods=['GET'])
def show_charts():
    no_nodes, miss_rate_list,hit_rate_list,no_items_list,total_size_list,no_request_list = aws_operations.get_statistics()
    return render_template('charts.html',no_nodes=no_nodes, miss_rate_list=miss_rate_list,hit_rate_list=hit_rate_list,no_items_list=no_items_list,total_size_list=total_size_list,no_request_list=no_request_list)

@webapp.route('/rebalance_keys', methods=['POST'])
def rebalance_keys():

    clear_2()

    all_keys = request.args.getlist('keys')
    size = request.args.get('size')
    user_id = request.args.get('user_id')
    
    img_dict = {}
    img_name_dict = {}

    for key in all_keys:
        # img_name = db_operations.get(key)
        url = LAMBDA_LOCATION_API + "/image"
        body = {
            "user_id": str(user_id),
            "key": str(key)
        }
        payload = json.dumps(body)
        
        result = requests.get(url, params=payload)
        img_name = result.json()['value']


        img_content = s3_bucket.get_image(str(img_name))
        image_b64 = base64.b64encode(img_content).decode("utf8")
        img_dict[str(key)] = image_b64
        img_name_dict[str(key)] = img_name
    
    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()
    while (len(running_ipv4_dict.keys()) != int(size)):
        time.sleep(1)
        running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()


    for key, img in img_dict.items():
        loc = request_routing.request_route(size, key)
        memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(loc)]) + ':5001/'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = json.dumps({"put_value": img, 'put_key': str(key), 'filename': str(img_name_dict[str(key)])})
        
        def retry(url, payload, headers):
            try:
                return requests.post(url, data=payload, headers=headers)
            except Exception:
                time.sleep(1)
                return retry(url, payload, headers)

        put_res = retry(str(memcache_loc) + 'put', payload, headers)
    

    return size


@webapp.route('/display_db_keys')
def display_db_keys():
    # result = db_operations.display_keys()
    url = LAMBDA_LOCATION_API + "/images"
    all_images = requests.get(url)
    
    result = []
    for img in all_images.json()['images']:
        result.append([img['key'], img['value']])

    return render_template("display_db_keys.html", pairs=result, where='database')


@webapp.route('/display_memcache_keys',methods=['POST'])
def display_memcache_keys():
    """
    Display all keys stored in MemCache
    """

    instance_id = request.form.get('instance_id')

    running_ipv4_dict = aws_operations.get_ec2_ip4_addresses()

    memcache_loc = 'http://' + str(running_ipv4_dict['memcache' + str(instance_id)]) + ':5001/'

    result = requests.get(str(memcache_loc + 'display_keys'))

    res = []
    for i in range(len(result.json())):
        res.append(result.json()[i])

    return render_template("display_keys_2.html", pairs=res, where='memcache')
