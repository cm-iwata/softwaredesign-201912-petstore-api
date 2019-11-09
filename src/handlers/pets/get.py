import logging
import os

import boto3

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

    res = pets_table.get_item(Key={'id': int(pet_id)})
    if 'Item' not in res:
        return HttpResponseUtil.pet_not_found()

    return HttpResponseUtil.ok(res['Item'])
