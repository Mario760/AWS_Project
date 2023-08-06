#!../venv/bin/python
from app import UPLOAD_FOLDER, webapp, memcache_ec2
import aws_operations


if __name__ == '__main__':
    print(aws_operations.start_memcache_ec2(0, 0))
    webapp.run('0.0.0.0', 5002, debug=True)