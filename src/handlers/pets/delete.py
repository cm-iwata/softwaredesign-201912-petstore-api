import logging
import os

import boto3
from botocore.client import ClientError

from decorators.handler_exception_decorator import handle_exception
from utils.http_response_util import HttpResponseUtil
from utils.validation_util import ValidationUtil

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])

logger = logging.getLogger()


@handle_exception(logger)
def handler(event, context):

    pet_id = event['pathParameters']['petId']
    if not ValidationUtil.is_integer(pet_id):
        return HttpResponseUtil.pet_not_found()

    try:
        pets_table.delete_item(
            Key={'id': int(pet_id)},
            ConditionExpression='attribute_exists(id)'
        )
        return HttpResponseUtil.no_content()
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') == 'ConditionalCheckFailedException':
            return HttpResponseUtil.pet_not_found()
        raise e
