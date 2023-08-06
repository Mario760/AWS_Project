from flask import Flask
import os
from collections import OrderedDict, deque

DEFAULT_CAPACITY = 1000
DEFAULT_POLICY = 'RR'

ROOT_FOLDER = '/home/ubuntu/ECE1779-Project/memcache/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')


global memcache, stats, dummy_stat, total_stat

cache = Flask(__name__)
cache.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cache.config['IMAGE_FOLDER'] = IMAGE_FOLDER
cache.config['CAPACITY'] = DEFAULT_CAPACITY
cache.config['POLICY'] = DEFAULT_POLICY


memcache = OrderedDict()
stats = deque()
# dummy_stat = {'no_items': 0,
#               'total_size': 0,
#               'no_request': 0,
#               'miss_rate': 0,
#               'hit_rate': 0
#               }
dummy_stat = {
              'no_request': 0,
              'miss_rate': 0,
              'hit_rate': 0
              }

total_stat = {
              'no_items': 0,
              'total_size': 0,
              'no_request': 0,
              'miss_rate': 0,
              'hit_rate': 0
              }

from app import main
