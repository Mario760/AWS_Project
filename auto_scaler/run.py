#!../venv/bin/python
from app import UPLOAD_FOLDER, auto_scaler




if __name__ == '__main__':
    # print(aws_operations.start_memcache_ec2(0, 0))
    auto_scaler.run('0.0.0.0', 5001, debug=False)