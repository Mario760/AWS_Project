#!../venv/bin/python
from app import UPLOAD_FOLDER, webapp
# import shutil
# import os
# import db_operations
# from aws_operations import Bucket

if __name__ == '__main__':
    # shutil.rmtree(UPLOAD_FOLDER)
    # os.mkdir(UPLOAD_FOLDER)
    # db_operations.initialize_images()
    # s3_bucket = Bucket('ece1779-project2-bucket0', 'us-east-1')



    webapp.run('0.0.0.0', 5000, debug=False)