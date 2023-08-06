from ctypes import sizeof
from flask import render_template, url_for, request
# import db_operations
from app import auto_scaler, memcache_ec2
from flask import json
import os, requests
import base64, sys
import aws_operations
import boto3

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


def check_img_name(filename: str) -> bool:
    """
    Check if file is an acceptable image.

    >>> check_image("XXX.jpg")
    True
    >>> check_image("XXX.pdf")
    False
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auto_scaler.route('/')
def main():
    return render_template("main.html")


@auto_scaler.route('/clear_memcache')
def clear_memcache():
    return render_template("clear_memcache.html")

@auto_scaler.route('/config_memcache')
def config_memcache():
    return render_template("config_memcache.html")

@auto_scaler.route('/get_memcache_stats')
def get_memcache_stat():
    return render_template("get_memcache_stats.html")

@auto_scaler.route('/resize_pool')
def resize_pool():
    return render_template("resize_pool.html")

@auto_scaler.route('/delete_all_data')
def delete_all_data():
    return render_template("delete_all_data.html")

@auto_scaler.route('/resize_pool_function',methods=['POST'])
def resize_pool_function():
    method = request.form.get('resize_method')
    curr_pool = len(list(aws_operations.get_ec2_ip4_addresses().values()))

    if method == "manual":
        return render_template("manual_resize_pool.html", pool_count=curr_pool)
    elif method == "automatic":
        return render_template("auto_resize_pool.html", pool_count=curr_pool)




@auto_scaler.route('/config_auto_scaler',methods=['POST'])
def config_auto_scaler():
    Max_Miss_Rate_threshold = request.args.get('Max_Miss_Rate_threshold')
    Min_Miss_Rate_threshold = request.args.get('Min_Miss_Rate_threshold')
    Ratio_by_which_to_expand_the_pool = request.args.get('Ratio_by_which_to_expand_the_pool')
    Ratio_by_which_to_shrink_the_pool = request.args.get('Ratio_by_which_to_shrink_the_pool')

    auto_scaler.config['Max_Miss_Rate_threshold'] = Max_Miss_Rate_threshold
    auto_scaler.config['Min_Miss_Rate_threshold'] = Min_Miss_Rate_threshold
    auto_scaler.config['Ratio_by_which_to_expand_the_pool'] = Ratio_by_which_to_expand_the_pool
    auto_scaler.config['Ratio_by_which_to_shrink_the_pool'] = Ratio_by_which_to_shrink_the_pool
    
    print("Max_Miss_Rate_threshold: ", auto_scaler.config['Max_Miss_Rate_threshold'])
    print("Min_Miss_Rate_threshold: ", auto_scaler.config['Min_Miss_Rate_threshold'])
    print("Ratio_by_which_to_expand_the_pool: ", auto_scaler.config['Ratio_by_which_to_expand_the_pool'])
    print("Ratio_by_which_to_shrink_the_pool: ", auto_scaler.config['Ratio_by_which_to_shrink_the_pool'])

    return "OK"

@auto_scaler.route('/config_manual_auto',methods=['POST'])
def config_manual_auto():
    manual_auto = request.args.get('mode')
    if str(manual_auto) == 'auto':
        auto_scaler.config['mode'] = 0
    elif str(manual_auto) == 'manual':
        auto_scaler.config['mode'] = 1
    else:
        print("Error")
    
    return "OK"
