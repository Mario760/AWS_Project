from re import L
from flask import render_template, url_for, request, send_file
from app import cache, memcache, dummy_stat, total_stat
from flask import json
import db_operations
import base64
import sys
import random

"'http://100.67.9.114:5002/'"
"'http://127.0.0.1:5002/'"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
FRONTEND_LOCATION = 'http://127.0.0.1:5000/'


def check_img_name(filename: str) -> bool:
    """
    Check if file is an acceptable image

    >>> check_image("XXX.jpg")
    True
    >>> check_image("XXX.pdf")
    False
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cache.route('/')
def main():
    
    return render_template("main.html")

@cache.route('/get',methods=['GET', 'POST'])
def get():
    dummy_stat['no_request'] += 1

    key = request.args.get('get_key')
    
    if key in memcache:
        dummy_stat['hit_rate'] += 1

        value = memcache[key]
        response = cache.response_class(
            response=json.dumps(str(value)),
            status=200,
            mimetype='application/json'
        )
        memcache.move_to_end(key)

    else:
        dummy_stat['miss_rate'] += 1

        response = cache.response_class(
            response=json.dumps('cache_miss'),
            status=200,
            mimetype='application/json'
        )

    return response

@cache.route('/put',methods=['POST'])
def put():

    # dummy_stat['no_items'] += 1
    total_stat['no_items'] += 1


    key = request.json['put_key']
    image_b64 = request.json['put_value']
    filename = request.json['filename']

    memcache[key] = image_b64

    img_bytes = base64.b64decode(image_b64.encode('utf-8'))

    # in case newly added image exceeds memcache capacity
    
    # total_size = dummy_stat['total_size'] + total_stat['total_size']

    rm_key_list = []

    total_size = total_stat['total_size']
    while (total_size > int(cache.config['CAPACITY'])  * 1000000 - sys.getsizeof(img_bytes)):
        key, val = None, None
        if cache.config['POLICY'] == 'RR':
            key, val = random.choice(list(memcache.items()))
            rm_key_list.append(str(key))
            memcache.pop(key)
        elif cache.config['POLICY'] == 'LRU':
            key, val = memcache.popitem(last=False)
            rm_key_list.append(str(key))
        
        removed_img = base64.b64decode(val.encode('utf-8'))
        total_size -= sys.getsizeof(removed_img)

        # dummy_stat['no_items'] -= 1
        # dummy_stat['total_size'] -= sys.getsizeof(removed_img)
        total_stat['no_items'] -= 1
        total_stat['total_size'] -= sys.getsizeof(removed_img)




    # dummy_stat['total_size'] += sys.getsizeof(img_bytes)
    total_stat['total_size'] += sys.getsizeof(img_bytes)

    response = cache.response_class(
        response=json.dumps("Successfully added key value pair {0} {1}".format(str(key), str(filename))),
        status=200,
        mimetype='application/json'
    )

    return json.dumps(rm_key_list)

@cache.route('/invalidateKey',methods=['GET','POST'])
def invalidateKey():
    key = request.args.get('key')

    rm_keys_list = []

    if key not in memcache.keys():
        # response = cache.response_class(
        #     response=json.dumps("Key not in memcache"),
        #     status=200,
        #     mimetype='application/json'
        # )
        return json.dumps(rm_keys_list)
    else:
        # dummy_stat['no_items'] -= 1
        total_stat['no_items'] -= 1

        img_bytes = base64.b64decode(memcache[key].encode('utf-8'))
        # dummy_stat['total_size'] -= sys.getsizeof(img_bytes)
        total_stat['total_size'] -= sys.getsizeof(img_bytes)

        memcache.pop(key)
        rm_keys_list.append(str(key))

        # response = cache.response_class(
        #     response=json.dumps(str("Succcessfully invalidated key " + key)),
        #     status=200,
        #     mimetype='application/json'
        # )
        return json.dumps(rm_keys_list)

    # return response

@cache.route('/clear',methods=['POST'])
def clear():
    for key in list(memcache.keys()):
        memcache.pop(key)

    # dummy_stat['no_items'] = 0
    # dummy_stat['total_size'] = 0
    total_stat['no_items'] = 0
    total_stat['total_size'] = 0

    response = cache.response_class(
        response=json.dumps("Succcessfully cleared all keys"),
        status=200,
        mimetype='application/json'
    )

    return response

@cache.route('/display_keys',methods=['GET','POST'])
def display_keys():
    
    res = []

    for key in memcache.keys():
        res.append([key])

    return json.dumps(res)

@cache.route('/get_all_keys',methods=['GET','POST'])
def get_all_keys():
    
    res = []

    for key in memcache.keys():
        res.append([key])

    return json.dumps(res)


@cache.route('/config_memcache',methods=['POST'])
def config_memcache():
    # id, capacity, policy = db_operations.get_config()

    capacity = request.args.get('capacity')
    policy = request.args.get('policy')

    cache.config['CAPACITY'] = capacity
    cache.config['POLICY'] = policy

    total_size = 0
    for value in memcache.values():
        img_bytes = base64.b64decode(value.encode('utf-8'))
        total_size += sys.getsizeof(img_bytes)

    while (total_size > int(cache.config['CAPACITY']) * 1000000):
        key, val = None, None
        if cache.config['POLICY'] == 'RR':
            key, val = random.choice(list(memcache.items()))
            memcache.pop(key)
        elif cache.config['POLICY'] == 'LRU':
            key, val = memcache.popitem(last=False)
        
        img_bytes = base64.b64decode(val.encode('utf-8'))
        total_size -= sys.getsizeof(img_bytes)

        # dummy_stat['no_items'] -= 1
        # dummy_stat['total_size'] -= sys.getsizeof(img_bytes)
        total_stat['no_items'] -= 1
        total_stat['total_size'] -= sys.getsizeof(img_bytes)
    

    response = cache.response_class(
        response=json.dumps("Successfully configured Capacity to {0}MB and Replacement Policy to {1}.".format(cache.config['CAPACITY'], cache.config['POLICY'])),
        status=200,
        mimetype='application/json'
    )

    return response

# @cache.route('/get_memcache_stats',methods=['GET','POST'])
# def get_memcache_stats():
    
#     return total_stat

if __name__ == "__main__":
    print(display_keys())
