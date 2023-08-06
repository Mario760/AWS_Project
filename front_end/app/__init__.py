from flask import Flask
import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import requests

# import db_operations
from aws_operations import Bucket



ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

ROOT_FOLDER = '/Users/Joey/Google_Drive/Year_1_1/ECE1779/Project_2/front_end/app'
IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, 'static/image')

LAMBDA_LOCATION_API = 'https://i3aj0vxx06.execute-api.us-east-1.amazonaws.com/user'


all_memcache_keys = []

webapp = Flask(__name__)
webapp.secret_key = 'secret-key'
webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webapp.config['IMAGE_FOLDER'] = IMAGE_FOLDER
# webapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
webapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/db.sqlite'

print(os.listdir('/tmp'))

if os.path.exists('/tmp/db.sqlite'):
    os.remove('/tmp/db.sqlite')
    print("Removed the file %s" % '/tmp/db.sqlite')

db = SQLAlchemy()
db.init_app(webapp)


from .models import User

with webapp.app_context():
    db.create_all()

# db_operations.initialize_images()
url = LAMBDA_LOCATION_API + "/images"
requests.delete(url)

url = LAMBDA_LOCATION_API + "/auth"
all_users = requests.get(url)

user_id_max = 0

for user in all_users.json()['users']:
    if int(user['user_id']) > user_id_max:
        user_id_max = int(user['user_id'])
    with webapp.app_context():
        new_user = User(username=str(user['username']), password=str(user['password']), user_id=str(user['user_id']))
        db.session.add(new_user)
        db.session.commit()


webapp.config['USER_ID_COUNT'] = user_id_max

s3_bucket = Bucket('ece1779-project2-bucket0', 'us-east-1')


login_manager = LoginManager()
login_manager.login_view = 'main'
login_manager.init_app(webapp)

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

from app import main

