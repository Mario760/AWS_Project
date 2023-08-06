import boto3
# from botocore.client import ClientError

ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

RDS_USERNAME = 'Joey'
RDS_PASSWORD = 'joey0101'

class Bucket(object):
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.conn = boto3.client('s3', 
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY, 
                        region_name=region
                    )

        if region != 'us-east-1':
            location = {'LocationConstraint': region}
            self.conn.create_bucket(Bucket=name, CreateBucketConfiguration=location)
        else:
            self.conn.create_bucket(Bucket=name)

    def put_image(self, file):
        self.conn.put_object(Bucket=self.name, Body = file, Key=file.filename)

    def get_image(self, filename):
        object = self.conn.get_object(Bucket=self.name, Key=filename)
        return object['Body'].read()
    
    def delete_image(self, filename):
        object = self.conn.delete_object(Bucket=self.name, Key=filename)

class RDS(object):
    def __init__(self, name, instance_class, region, storage):
        self.name = name
        self.region = region
        self.storage = storage
        self.instance_class = instance_class
        self.conn = boto3.client('rds',
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY, 
                        region_name=region
                    )

        repeat_db = False
        list_db = self.conn.describe_db_instances()['DBInstances']
        for db in list_db:
            if db['DBInstanceIdentifier'] == name:
                repeat_db = True
                break
        
        if not repeat_db:
            self.conn.create_db_instance(
                AllocatedStorage=storage,
                DBInstanceClass=instance_class,
                DBInstanceIdentifier=name,
                Engine='MySQL',
                MasterUsername=RDS_USERNAME,
                MasterUserPassword=RDS_PASSWORD,
            )
    
    def start_instance(self):
        self.conn.start_db_instance(DBInstanceIdentifier=self.name)

    def stop_instance(self):
        self.conn.stop_db_instance(DBInstanceIdentifier=self.name)

    def delete_instance(self):
        self.conn.delete_db_instance(
            DBInstanceIdentifier=self.name,
            SkipFinalSnapshot=True,
        )

def get_ec2_ip4_addresses(region='us-east-1') -> list:
    conn = boto3.resource('ec2',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    
    memcache_dict = {}

    for instance in conn.instances.all():
        if (instance.state['Name'] == 'running' and 'memcache' in instance.tags[0]['Value']):
            memcache_dict[instance.tags[0]['Value']] = instance.public_ip_address

            # print(
            #     "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
            #     instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
            #     )
            # )
    return memcache_dict




if __name__ == '__main__':
    s3_bucket = Bucket('ece1779-project2-bucket0', 'us-east-1')
    img = s3_bucket.get_image('IMG_7573.jpeg')
    print(img)

    

    
    
