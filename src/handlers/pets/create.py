import json
import os

import boto3

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


def handler(event, context):

    data = json.loads(event['body'])
    pets_table.put_item(Item=data)

    return {
      'statusCode': 201,
      'body': json.dumps(data)
    }
