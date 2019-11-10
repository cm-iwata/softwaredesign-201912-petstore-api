from http import HTTPStatus
import os

import boto3
import pytest

from handlers.pets.list import handler
from src.utils.json_util import JsonUtil

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


@pytest.mark.usefixtures('create_pets_table')
def test_no_pets_will_return_empty_pet_list():

    event = {
        'queryStringParameters': None,
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pets = JsonUtil.loads(res['body'])
    assert pets == []


@pytest.mark.usefixtures('create_pets_table')
def test_return_pets_list():

    pets_table.put_item(Item={
        'id': 1,
        'name': 'dog',
    })

    pets_table.put_item(Item={
        'id': 2,
        'name': 'cat',
        'tags': [{
            'id': 1,
            'name': 'some tag'
        }]
    })

    event = {
        'queryStringParameters': None,
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pets = JsonUtil.loads(res['body'])
    assert len(pets) == 2

    assert pets[0]['id'] == 1
    assert pets[0]['name'] == 'dog'

    assert pets[1]['id'] == 2
    assert pets[1]['name'] == 'cat'
    assert pets[1]['tags'][0]['id'] == 1
    assert pets[1]['tags'][0]['name'] == 'some tag'


@pytest.mark.usefixtures('create_pets_table')
def test_non_limit_param_will_return_100pets():

    for i in range(101):
        pets_table.put_item(Item={
            'id': i + 1,
            'name': f'pet{i + 1}',
        })

    event = {
        'queryStringParameters': None,
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pets = JsonUtil.loads(res['body'])
    assert len(pets) == 100
    x_next = res['headers']['x-next']
    assert x_next == '<https://1234567890.execute-api.us-east-1.amazonaws.com/prod/pets?' \
                     'last_evaluated_key=100>; rel="next"'


@pytest.mark.usefixtures('create_pets_table')
@pytest.mark.parametrize('limit', [
    1, 10, 20, 30, 40, 55, 99, 100
])
def test_limit_param_will_restrict_return_pets(limit):

    for i in range(101):
        pets_table.put_item(Item={
            'id': i + 1,
            'name': f'pet{i + 1}',
        })

    event = {
        'queryStringParameters': {
            'limit': limit
        },
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pets = JsonUtil.loads(res['body'])
    assert len(pets) == limit
    x_next = res['headers']['x-next']
    str_limit = str(limit)
    assert x_next == '<https://1234567890.execute-api.us-east-1.amazonaws.com/prod/pets?' \
                     f'limit={str_limit}&last_evaluated_key={str_limit}>; rel="next"'


@pytest.mark.usefixtures('create_pets_table')
@pytest.mark.parametrize('last_evaluated_key, expect_pets_len', [
    ('1', 99),
    ('10', 90),
    ('20', 80),
    ('30', 70),
    ('45', 55),
    ('99', 1),
    ('100', 0),
])
def test_last_evaluated_key(last_evaluated_key, expect_pets_len):

    for i in range(100):
        pets_table.put_item(Item={
            'id': i + 1,
            'name': f'pet{i + 1}',
        })

    event = {
        'queryStringParameters': {
            'last_evaluated_key': last_evaluated_key
        },
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pets = JsonUtil.loads(res['body'])
    assert len(pets) == expect_pets_len


@pytest.mark.parametrize('query_string_param, expect_msg', [
    (
            {'limit': 'str val'},
            {'limit': ['must be integer']}
    ),
    (
            {'limit': '１'},
            {'limit': ['must be integer']}
    ),
    (
            {'limit': '0'},
            {'limit': ["min value is 1"]}
    ),
    (
            {'limit': '101'},
            {'limit': ["max value is 100"]}
    ),
    (
            {'last_evaluated_key': 'str val'},
            {'last_evaluated_key': ['must be integer']}
    ),
    (
            {'last_evaluated_key': 'Ⅰ'},
            {'last_evaluated_key': ['must be integer']}
    ),
])
def test_invalid_qs_will_return_bad_request(query_string_param, expect_msg):

    event = {
        'queryStringParameters': query_string_param,
        'headers': {
            'Host': '1234567890.execute-api.us-east-1.amazonaws.com',
            'X-Forwarded-Proto': 'https'
        },
        'requestContext': {
            'path': '/prod/pets'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.BAD_REQUEST
    body = JsonUtil.loads(res['body'])
    assert body['message'] == expect_msg
