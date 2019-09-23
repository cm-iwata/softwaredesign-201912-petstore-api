import json
from json.decoder import JSONDecodeError
import os

import boto3
from botocore.exceptions import ClientError
from cerberus import Validator

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])
schema = {
    'id': {
        'type': 'integer',
        'required': True,
        'min': 1,
    },
    'name': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 50,
        'required': True,
    },
    'tags': {
        'type': 'list',
        'required': False,
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {
                    'type': 'integer',
                    'required': True,
                },
                'name': {
                    'type': 'string',
                    'minlength': 1,
                    'maxlength': 50,
                    'required': True,
                }
            }
        }
    }
}


def handler(event, context):

    if not __is_valid_json(event['body']):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': "request body doesn't contain valid json"
            })
        }

    data = json.loads(event['body'])
    v = Validator(schema)
    if v.validate(data) is not True:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': v.errors
            })
        }

    try:
        pets_table.put_item(Item=data,
                            ConditionExpression='attribute_not_exists(id)')
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':
            return {
                'statusCode': 409,
                'body': json.dumps({
                    'message': 'the specified id is already exists'
                })
            }
        raise

    return {
      'statusCode': 201,
      'body': json.dumps(data)
    }


def __is_valid_json(src):
    if src is None:
        return False

    try:
        res = json.loads(src)
        if isinstance(res, dict) or isinstance(res, list):
            return True
        return False
    except JSONDecodeError:
        return False
