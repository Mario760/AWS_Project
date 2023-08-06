from flask import Flask
import os

ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_2/manager_app/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

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


webapp = Flask(__name__)
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['IMAGE_FOLDER'] = IMAGE_FOLDER
webapp.config['CAPACITY'] = 1000
webapp.config['POLICY'] = 'RR'

from app import main
