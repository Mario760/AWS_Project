import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_USER_INFO = 'user_info'
TABLE_USER_AUTH = 'user_auth'
TABLE_IMAGE = 'image'

dynamodb = boto3.resource('dynamodb')
table_user_info = dynamodb.Table(TABLE_USER_INFO)
table_user_auth = dynamodb.Table(TABLE_USER_AUTH)
table_image = dynamodb.Table(TABLE_IMAGE)



getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
userPath = '/user'
authPath = '/auth'
usersPath = '/users'
imagePath = '/image'
imagesPath = '/images'

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == userPath:
        response = getUser(event['queryStringParameters']['user_id'])
    elif httpMethod == getMethod and path == usersPath:
        response = getUsers()
    elif httpMethod == getMethod and path == authPath:
        response = getUsersAuth()
        
    elif httpMethod == postMethod and path == userPath:
        requestBody = json.loads(event['body'])
        response = createUser(requestBody['user_info'], requestBody['user_auth'])
    
    elif httpMethod == patchMethod and path == userPath:
        requestBody = json.loads(event['body'])
        response = modifyUser(requestBody['user_id'], requestBody['update_key'], requestBody['update_value'])
    
    elif httpMethod == postMethod and path == authPath:
        requestBody = json.loads(event['body'])
        response = authenticateUser(requestBody['username'], requestBody['password'])
    elif httpMethod == patchMethod and path == authPath:
        requestBody = json.loads(event['body'])
        response = modifyUserAuth(requestBody['username'], requestBody['update_key'], requestBody['update_value'])
    
    elif httpMethod == deleteMethod and path == userPath:
        requestBody = json.loads(event['body'])
        response = deleteUser(requestBody['user_id'])

    elif httpMethod == getMethod and path == imagePath:
        response = getImage(event['queryStringParameters']['user_id'], event['queryStringParameters']['key'])
    elif httpMethod == getMethod and path == imagesPath:
        response = getImages()
    
    elif httpMethod == deleteMethod and path == imagePath:
        requestBody = json.loads(event['body'])
        response = deleteImage(requestBody['user_id'], requestBody['key'])

    elif httpMethod == postMethod and path == imagePath:
        requestBody = json.loads(event['body'])
        response = putImage(requestBody['image_info'])

    elif httpMethod == deleteMethod and path == imagesPath:
        response = deleteImages()

    
    else:
        response = buildResponse(404, 'Not Found')
    
    return response
    

def getUser(user_id):
    try:
        response = table_user_info.get_item(
            Key = {
                'user_id': user_id
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'UserID: %s not found' % user_id})
    
    except:
        logger.exception('getUser function error!')

def getImage(user_id, key):
    try:
        response = table_image.get_item(
            Key = {
                'user_id': user_id,
                'key': key
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'ImageKey: %s not found' % key})
    
    except:
        logger.exception('getImage function error!')
        
def getUsers():
    try:
        response = table_user_info.scan()
        result = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table_user_info.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Item'])
        
        body = {
            'users': result
        }         
        return buildResponse(200, body)
        
    except:
        logger.exception('getUsers function error!')

def getUsersAuth():
    try:
        response = table_user_auth.scan()
        result = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table_user_auth.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Item'])
        
        body = {
            'users': result
        }         
        return buildResponse(200, body)
        
    except:
        logger.exception('getUsers function error!')

def getImages():
    try:
        response = table_image.scan()
        result = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table_image.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
            result.extend(response['Item'])
        
        body = {
            'images': result
        }         
        return buildResponse(200, body)
        
    except:
        logger.exception('getImages function error!')
        
def createUser(user_info, user_auth):
    try:
        table_user_info.put_item(Item = user_info)
        table_user_auth.put_item(Item = user_auth)
        body = {
            'Operation': 'createUser',
            'Message': 'SUCCESS',
            'Item': user_info
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('createUser function error!')

def putImage(image_info):
    try:
        table_image.put_item(Item = image_info)
        body = {
            'Operation': 'putImage',
            'Message': 'SUCCESS',
            'Item': image_info
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('putImage function error!')
        
def modifyUser(user_id, update_key, update_value):
    try:
        response = table_user_info.update_item(
            Key = {
                'user_id': user_id
            },
            UpdateExpression = 'set %s = :value' % update_key,
            ExpressionAttributeValues = {
                ':value': update_value
            },
            ReturnValues = 'UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('modifyUser function error!')
        
def authenticateUser(username, password):
    try:
        response = table_user_auth.get_item(
            Key = {
                'username': username
            }
        )
    
        if 'Item' in response:
            if response['Item']['password'] == password and response['Item']['isAdmin'] == "true":
                return buildResponse(210, {'Message': 'Admin Login', 'LoginCode': '210'})
            elif response['Item']['password'] == password and response['Item']['isAdmin'] == "false":
                return buildResponse(200, {'Message': 'Login for username %s successful!' % username, 'LoginCode': '200'})
            else:
                return buildResponse(201, {'Message': 'Password for username %s is incorrect!' % username, 'LoginCode': '201'})
        else:
            return buildResponse(202, {'Message': 'Username %s not found' % username, 'LoginCode': '202'})
    
    except:
        logger.exception('getUser function error!')
        
def modifyUserAuth(username, update_key, update_value):
    try:
        response = table_user_auth.update_item(
            Key = {
                'username': username
            },
            UpdateExpression = 'set %s = :value' % update_key,
            ExpressionAttributeValues = {
                ':value': update_value
            },
            ReturnValues = 'UPDATED_NEW'
        )
        
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('modifyUserAuth function error!')
        
def deleteUser(user_id):
    try:
        response = table_user_info.delete_item(
            Key = {
                'user_id': user_id
            },
            ReturnValues = 'ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('deleteUser function error!')

def deleteImage(user_id, key):
    try:
        response = table_image.delete_item(
            Key = {
                'user_id': user_id,
                'key': key
            },
            ReturnValues = 'ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('deleteImage function error!')

def deleteImages():
    try:

       
        scan = table_image.scan()
        with table_image.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(
                    Key={
                        'user_id': each['user_id'],
                        'key': each['key']
                    }
                ) 
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS'
        }
        return buildResponse(200, body)
    
    except:
        logger.exception('deleteImage function error!')











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