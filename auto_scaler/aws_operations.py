import boto3
import datetime

ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

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





def get_cloudwatch_stats(instance_id: int, region='us-east-1', period=60) -> dict:
    conn = boto3.client('cloudwatch',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    metric_list = ['no_items', 'total_size', 'no_request', 'miss_rate', 'hit_rate']

    metric_stats = {}

    for metric in metric_list:
        metric_stats[metric] = conn.get_metric_statistics(
                                    Namespace = 'MemCache_NameSpace',
                                    Period = period,
                                    StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = period),
                                    EndTime = datetime.datetime.utcnow(),
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







def start_memcache_ec2(start: int, end:int, region='us-east-1') -> list:
    if start > end:
        return "Already maximum instance"
    
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
    if start > end:
        return "Already minimum instance"
    
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

if __name__ == "__main__":
    # s3_bucket = Bucket('ece1779-project2-bucket0', 'us-east-1')
    # s3_bucket.delete_all_images()
    # memcache_ec2 = start_memcache_ec2(1,3)
    # print(memcache_ec2)

    cloudwatch_dict = get_cloudwatch_stats(0)
    print(cloudwatch_dict['no_request']['Datapoints'][0]['Average'])