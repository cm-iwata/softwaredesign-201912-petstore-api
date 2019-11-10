import logging
import os

import boto3
from cerberus import Validator

from decorators.handler_exception_decorator import handle_exception
from utils.http_response_util import HttpResponseUtil
from utils.validation_util import ValidationUtil


def _validate_integer(field, value, error):
    if not ValidationUtil.is_integer(str(value), allow_zero=True):
        error(field, 'must be integer')
        return False
    return True


def _validate_limit(field, value, error):

    if not _validate_integer(field, value, error):
        return

    if int(value) < 1:
        return error(field, 'min value is 1')

    if int(value) > 100:
        return error(field, 'max value is 100')


def _validate_lek(field, value, error):
    _validate_integer(field, value, error)


dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])

logger = logging.getLogger()
schema = {
    'limit': {
        'required': False,
        'check_with': _validate_limit
    },
    'last_evaluated_key': {
        'required': False,
        'check_with': _validate_lek,
    }
}


@handle_exception(logger)
def handler(event, context):

    query_strings = event['queryStringParameters'] \
        if event['queryStringParameters'] else {}

    v = Validator(schema)
    if v.validate(query_strings) is not True:
        return HttpResponseUtil.bad_request(v.errors)

    limit = query_strings.get('limit', 100)
    param = {'Limit': int(limit)}
    if 'last_evaluated_key' in query_strings:
        param['ExclusiveStartKey'] = {
            'id': int(query_strings['last_evaluated_key'])
        }

    res = pets_table.scan(**param)

    headers = {}
    if 'LastEvaluatedKey' in res:
        headers['x-next'] = _generate_next_link(
            event, query_strings, res['LastEvaluatedKey'])

    return HttpResponseUtil.ok(res['Items'], headers)


def _generate_next_link(event, query_strings, le_key):
    last_id = str(le_key['id'])

    request_headers = event['headers']
    proto = request_headers['X-Forwarded-Proto']
    host = request_headers['Host']
    path = event['requestContext']['path']

    query_strings['last_evaluated_key'] = last_id
    query_strings = '&'.join(f'{key}={value}'
                             for key, value in query_strings.items())

    return f'<{proto}://{host}{path}?{query_strings}>; rel="next"'
