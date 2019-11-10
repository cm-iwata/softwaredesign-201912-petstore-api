import os
from http import HTTPStatus

import boto3
import pytest

from handlers.pets.update import handler
from utils.json_util import JsonUtil

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


@pytest.mark.usefixtures('create_pets_table')
def test_non_exists_id_will_return_not_found():

    event = {
        'pathParameters': {
            'petId': '1'
        },
        'body': JsonUtil.dumps({
            'name': 'cat'
        })
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('create_pets_table')
def test_valid_data_will_update_pet():

    pets_table.put_item(Item={
        'id': 1,
        'name': 'dog'
    })

    event = {
        'pathParameters': {
            'petId': '1'
        },
        'body': JsonUtil.dumps({
            'name': 'cat',
            'tags': [
                {
                    'id': 1,
                    'name': 'some tag'
                }
            ]
        })
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    data = JsonUtil.loads(res['body'])
    assert data['id'] == 1
    assert data['name'] == 'cat'
    assert data['tags'][0]['id'] == 1
    assert data['tags'][0]['name'] == 'some tag'

    dynamo_res = pets_table.get_item(Key={'id': 1})
    assert 'Item' in dynamo_res
    item = dynamo_res['Item']
    assert item['id'] == 1
    assert item['name'] == 'cat'
    assert item['tags'][0]['id'] == 1
    assert item['tags'][0]['name'] == 'some tag'


@pytest.mark.usefixtures('create_pets_table')
def test_invalid_pet_id_will_return_not_found():

    event = {
        'pathParameters': {
            'petId': 'str val'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('data,res_body', [
    (
            'invalid_json',
            '{"message": "request body doesn\'t contain valid json"}'
    ),
    (
            {},
            '{"message": {"name": ["required field"]}}'
    ),
    (
            {'name': ''},
            '{"message": {"name": ["min length is 1"]}}'
    ),
    (
            {'name': '123456789012345678901234567890123456789012345678901'},
            '{"message": {"name": ["max length is 50"]}}'
    ),
    (
            {'name': 'dog', 'tags': [{'id': 1}]},
            '{"message": {"tags": [{"0": [{"name": ["required field"]}]}]}}'
    ),
    (
            {'name': 'dog', 'tags': [{'id': 1, 'name': ''}]},
            '{"message": {"tags": [{"0": [{"name": ["min length is 1"]}]}]}}'
    ),
    (
            {'name': 'dog', 'tags': [
                {'id': 1, 'name': '123456789012345678901234567890123456789012345678901'}]
             },
            '{"message": {"tags": [{"0": [{"name": ["max length is 50"]}]}]}}'
    ),
    (
            {'name': 'dog', 'tags': []},
            '{"message": {"tags": ["min length is 1"]}}'
    ),
    (
            {'name': 'dog', 'tags': [
                {'id': 1, 'name': 'a'},
                {'id': 2, 'name': 'b'},
                {'id': 3, 'name': 'c'},
                {'id': 4, 'name': 'd'},
                {'id': 5, 'name': 'e'},
                {'id': 6, 'name': 'f'},
                {'id': 7, 'name': 'g'},
                {'id': 8, 'name': 'h'},
                {'id': 9, 'name': 'i'},
                {'id': 10, 'name': 'j'},
                {'id': 11, 'name': 'k'}
            ]},
            '{"message": {"tags": ["max length is 10"]}}'
    ),
])
def test_invalid_json_will_return_bad_request(data, res_body):

    event = {
        'pathParameters': {
            'petId': '1'
        },
        'body': JsonUtil.dumps(data)
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.BAD_REQUEST
    assert res['body'] == res_body
