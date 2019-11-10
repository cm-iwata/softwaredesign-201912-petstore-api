import os
import logging

import boto3
from botocore.exceptions import ClientError
from cerberus import Validator

from decorators.handler_exception_decorator import handle_exception
from utils.http_response_util import HttpResponseUtil
from utils.json_util import JsonUtil
from utils.validation_util import ValidationUtil


dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])
schema = {
    'name': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 50,
        'required': True,
    },
    'tags': {
        'type': 'list',
        'required': False,
        'minlength': 1,
        'maxlength': 10,
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

logger = logging.getLogger()


@handle_exception(logger)
def handler(event, context):

    pet_id = event['pathParameters']['petId']
    if not ValidationUtil.is_integer(pet_id):
        return HttpResponseUtil.pet_not_found()

    if not JsonUtil.is_valid_json(event['body']):
        return HttpResponseUtil.bad_request("request body doesn't contain valid json")

    data = JsonUtil.loads(event['body'])
    v = Validator(schema)
    if v.validate(data) is not True:
        return HttpResponseUtil.bad_request(v.errors)

    pet = {'id': int(pet_id), **data}
    try:
        pets_table.put_item(Item=pet,
                            ConditionExpression='attribute_exists(id)')

    except ClientError as e:
        if e.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':
            return HttpResponseUtil.pet_not_found()
        raise

    return HttpResponseUtil.ok(pet)
