import json
import boto3
import logging
from custom_encoder import CustomEncoder
dynamodb = boto3.resource('dynamodb')
table_image = dynamodb.Table('image')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
client = boto3.client("rekognition")

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    print(httpMethod)
    print(path)
    if httpMethod == 'GET' and path == '/labels':
        print("something")
        response = getLabels(event['queryStringParameters']['user_id'], event['queryStringParameters']['key'])
    elif httpMethod == 'GET' and path == '/text':
        response = getText(event['queryStringParameters']['user_id'], event['queryStringParameters']['key'])
    
    return response
    
def getLabels(id_num, key):
    image = getImageName(id_num, key)
    print(image)
    if image != "":
        #This will detect the item in the image
        response = client.detect_labels(Image = {"S3Object": {"Bucket":"ece1779-project2-bucket0","Name":image}}, MaxLabels = 10)
        results = []
        for label in response['Labels']:
            results.append("This is a : " + label['Name']+" with confidence "+ "{:.2f}".format(label['Confidence']) + "%")
        if len(results)==0:
            results.append("Cannot Detect Any Label")
        return buildResponse(200, {'image':image, 'result':results})
    else:
        return buildResponse(404, {'Message': 'ImageKey: %s not found' % key})

def getText(id_num, key):        
    # This will detect the text in the image
    image = getImageName(id_num, key)
    if image != "":
        results = []
        response = client.detect_text(Image = {"S3Object": {"Bucket":"ece1779-project2-bucket0","Name":image}})
        textDetections=response['TextDetections']
        for text in textDetections:
            results.append('Detected text:' + text['DetectedText'])
        if  len(results)==0:
            results.append("Cannot Detect Any Text")
        return buildResponse(200, {'image':image, 'result':results})
    else:
        return buildResponse(404, {'Message': 'ImageKey: %s not found' % key})

def getImageName(user_id, key):
    try:
        response = table_image.get_item(
            Key = {
                'user_id': user_id,
                'key': key
            }
        )
        if 'Item' in response:
            return response['Item']['value']
        else:
            return ""
    
    except:
        logger.exception('getImage function error!')

    
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
