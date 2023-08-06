import boto3
import datetime


ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

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

    def delete_all_images(self):
        if 'Contents' in self.conn.list_objects(Bucket=self.name).keys():
            for key in self.conn.list_objects(Bucket=self.name)['Contents']:
                self.conn.delete_object(Bucket=self.name, Key=key['Key'])
                print(key['Key'])
        else:
            print("Empty S3!")
    
    def delete_image(self, filename):
        pass

def get_ec2_ip4_addresses(region='us-east-1') -> dict:
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




def get_cloudwatch_stats_2_3_4(instance_id: int, starttime=datetime.datetime.utcnow() - datetime.timedelta(seconds = 60), endtime=datetime.datetime.utcnow(), region='us-east-1', period=60) -> dict:
    conn = boto3.client('cloudwatch',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    metric_list = ['no_request', 'miss_rate', 'hit_rate']

    metric_stats = {}

    for metric in metric_list:
        metric_stats[metric] = conn.get_metric_statistics(
                                    Namespace = 'MemCache_NameSpace',
                                    Period = period,
                                    StartTime = starttime,
                                    EndTime = endtime,
                                    MetricName = 'MemCache_Stats_' + metric,
                                    Statistics=['Sum'], Unit='None',
                                    Dimensions = [
                                        {
                                            'Name': 'Instance Name',
                                            'Value': str(instance_id)
                                        }
                                    ]
                                )
    
    return metric_stats


# Cumulative
def get_cloudwatch_stats_0_1(instance_id: int, starttime=datetime.datetime.utcnow() - datetime.timedelta(seconds = 60), endtime=datetime.datetime.utcnow(), region='us-east-1', period=60) -> dict:
    conn = boto3.client('cloudwatch',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    metric_list = ['no_items', 'total_size']

    metric_stats = {}

    for metric in metric_list:
        metric_stats[metric] = conn.get_metric_statistics(
                                    Namespace = 'MemCache_NameSpace',
                                    Period = period,
                                    StartTime = starttime,
                                    EndTime = endtime,
                                    MetricName = 'MemCache_Stats_' + metric,
                                    Statistics=['Average'], Unit='None',
                                    Dimensions = [
                                        {
                                            'Name': 'Instance Name',
                                            'Value': str(instance_id)
                                        }
                                    ]
                                )
    
    return metric_stats





def start_memcache_ec2(start: int, end:int, region='us-east-1') -> list:
    conn = boto3.resource('ec2',
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY, 
                region_name=region
            )

    ec2 = boto3.client('ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY, 
                region_name=region
            )

    memcache_ec2 = []
    # memcache_dict = {}

    for instance in conn.instances.all():
        if 'memcache' in instance.tags[0]['Value'] and instance.state['Name'] == 'stopped' and int(instance.tags[0]['Value'][8]) >= start and int(instance.tags[0]['Value'][8]) <= end:
            memcache_ec2.append(instance)
    
    if len(memcache_ec2):
        ec2.start_instances(InstanceIds=[instance.id for instance in memcache_ec2])
        

    # for instance in memcache_ec2:
    #     memcache_dict[instance.tags[0]['Value']] = instance.public_ip_address
    
    return "Successfully started memcache{0} to memcache{1}.".format(start, end)
    
def stop_memcache_ec2(start: int, end:int, region='us-east-1') -> list:
    conn = boto3.resource('ec2',
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY, 
                region_name=region
            )

    ec2 = boto3.client('ec2', 
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY, 
                region_name=region
            )

    memcache_ec2 = []
    # memcache_dict = {}

    for instance in conn.instances.all():
        if 'memcache' in instance.tags[0]['Value'] and instance.state['Name'] == 'running' and int(instance.tags[0]['Value'][8]) >= start and int(instance.tags[0]['Value'][8]) <= end:
            memcache_ec2.append(instance)
    
    if len(memcache_ec2):
        ec2.stop_instances(InstanceIds=[instance.id for instance in memcache_ec2])
        

    # for instance in memcache_ec2:
    #     memcache_dict[instance.tags[0]['Value']] = instance.public_ip_address

    return "Successfully stopped memcache{0} to memcache{1}.".format(start, end)

def get_statistics():
    no_nodes = []
    miss_rate_list = []
    hit_rate_list = []
    no_items_list = []
    total_size_list =[]
    no_request_list = []

    for minute in range(30,0,-1):
        items_sublst, size_sublst, request_sublst, mr_sublst, hr_sublst = [],[],[],[],[]
        nodes = 0
        for instance_id in range(0,8):
            cloudwatch_dict_1 = get_cloudwatch_stats_0_1(instance_id, datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*minute), datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*(minute-1)))
            if len(cloudwatch_dict_1['no_items']['Datapoints']) == 0:
                continue
            nodes = nodes + 1
            items_sublst.append(cloudwatch_dict_1['no_items']['Datapoints'][0]['Average'])
            size_sublst.append(cloudwatch_dict_1['total_size']['Datapoints'][0]['Average'])

            cloudwatch_dict_2 = get_cloudwatch_stats_2_3_4(instance_id, datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*minute), datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*(minute-1)))
            no_request = cloudwatch_dict_2['no_request']['Datapoints'][0]['Sum']
            request_sublst.append(no_request)
            if no_request != 0 :
                mr_sublst.append(cloudwatch_dict_2['miss_rate']['Datapoints'][0]['Sum']/no_request)
                hr_sublst.append(cloudwatch_dict_2['hit_rate']['Datapoints'][0]['Sum']/no_request)
            else:
                mr_sublst.append(0)
                hr_sublst.append(0)
        miss_rate_list.append(sum(mr_sublst)/len(mr_sublst))
        hit_rate_list.append(sum(hr_sublst)/len(hr_sublst))
        no_items_list.append(sum(items_sublst)/len(items_sublst))
        total_size_list.append(sum(size_sublst)/len(size_sublst))
        no_request_list.append(sum(request_sublst)/len(request_sublst))
        no_nodes.append(nodes)

    return no_nodes, miss_rate_list,hit_rate_list,no_items_list,total_size_list,no_request_list

if __name__ == "__main__":
    # s3_bucket = Bucket('ece1779-project2-bucket0', 'us-east-1')
    # s3_bucket.delete_all_images()
    # memcache_ec2 = start_memcache_ec2(1,3)
    # print(memcache_ec2)
    # ipv4_dict = get_ec2_ip4_addresses()
    # print(ipv4_dict)

    miss_rate_list = []
    hit_rate_list = []
    no_items_list = []
    total_size_list =[]
    no_request_list = []
    for minute in range(30,0,-1):
        cloudwatch_dict_1 = get_cloudwatch_stats_0_1(0, datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*minute), datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*(minute-1)))
        no_items_list.append(cloudwatch_dict_1['no_items']['Datapoints'][0]['Average'])
        total_size_list.append(cloudwatch_dict_1['total_size']['Datapoints'][0]['Average'])

        cloudwatch_dict_2 = get_cloudwatch_stats_2_3_4(0, datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*minute), datetime.datetime.utcnow() - datetime.timedelta(seconds = 60*(minute-1)))
        miss_rate_list.append(cloudwatch_dict_2['miss_rate']['Datapoints'][0]['Sum'])
        hit_rate_list.append(cloudwatch_dict_2['hit_rate']['Datapoints'][0]['Sum'])
        no_request_list.append(cloudwatch_dict_2['no_request']['Datapoints'][0]['Sum'])
    print(no_items_list)
