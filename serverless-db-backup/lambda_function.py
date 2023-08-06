import boto3
import json
import logging
import datetime
from custom_encoder import CustomEncoder

MAX_BACKUPS = 3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')

getMethod = 'GET'
postMethod = 'POST'

healthPath = '/health'
tablePath = '/table'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
        
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)

    elif httpMethod == postMethod and path == tablePath:
        requestBody = json.loads(event['body'])
        response = createBackup(requestBody['table_name'])
    
    else:
        response = buildResponse(404, 'Not Found')
    
    return response

def createBackup(table_name):
    try:
        backup_name = table_name + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        response = dynamodb.create_backup(
            TableName = table_name,
            BackupName = backup_name
        )
        deleteBackup(table_name)
        return buildResponse(200, json.loads(json.dumps(response['BackupDetails'], default=str)))
        # print(json.loads(json.dumps(response['BackupDetails'], default=str)))
        # return (json.loads(json.dumps(response['BackupDetails'], default=str)))
    except:
        logger.exception('createBackup function error!')

def deleteBackup(table_name):
    backups = dynamodb.list_backups(
        TableName=table_name
    )

    backup_count = len(backups['BackupSummaries'])

    if backup_count <= MAX_BACKUPS:
        return

    sorted_list = sorted(backups['BackupSummaries'],
                         key=lambda k: k['BackupCreationDateTime'])

    old_backups = sorted_list[:MAX_BACKUPS]

    for backup in old_backups:
        arn = backup['BackupArn']
        print("ARN to delete: " + arn)
        deleted_arn = dynamodb.delete_backup(BackupArn=arn)
        status = deleted_arn['BackupDescription']['BackupDetails']['BackupStatus']
        print("Status:", status)



def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
        
    return response


