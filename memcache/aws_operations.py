import boto3

ACCESS_KEY = 'AKIAYXTIZC27HZD67VO7'
SECRET_KEY = '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'

def post_custom_metric(region: str, instance_id: int, stats: dict):
    conn = boto3.client('cloudwatch',
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY, 
                    region_name=region
                )
    metric_list = ['no_items', 'total_size', 'no_request', 'miss_rate', 'hit_rate']
    for metric in metric_list:
        conn.put_metric_data(
            MetricData = [
                {
                    'MetricName': 'MemCache_Stats_' + metric,
                    'Dimensions': [
                        {
                            'Name': 'Instance Name',
                            'Value': str(instance_id)
                        },
                    ],
                    'Unit': 'None',
                    'Value': stats[metric],
                    'StorageResolution': 1
                },
            ],
            Namespace = 'MemCache_NameSpace',
        )
    

if __name__ == '__main__':

    post_custom_metric('us-east-1', 3, 30, 2, 0.5, 0.5)