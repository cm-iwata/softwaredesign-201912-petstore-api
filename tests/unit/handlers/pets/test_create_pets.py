import os
from http import HTTPStatus

import boto3
import pytest

from handlers.pets.create import handler
from utils.json_util import JsonUtil

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


@pytest.mark.usefixtures('create_pets_table')
def test_valid_data_will_creates_pet():

    event = {
        'body': JsonUtil.dumps({
            'id': 1,
            'name': 'dog',
            'tags': [
                {
                    'id': 1,
                    'name': 'some tag'
                }
            ]
        })
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.CREATED
    data = JsonUtil.loads(res['body'])
    assert data['id'] == 1
    assert data['name'] == 'dog'
    assert data['tags'][0]['id'] == 1
    assert data['tags'][0]['name'] == 'some tag'

    dynamo_res = pets_table.get_item(Key={'id': 1})
    assert 'Item' in dynamo_res
    item = dynamo_res['Item']
    assert item['id'] == 1
    assert item['name'] == 'dog'


@pytest.mark.parametrize('data,res_body', [
    (
            'invalid_json',
            '{"message": "request body doesn\'t contain valid json"}'
    ),
    (
            {'id': 1},
            '{"message": {"name": ["required field"]}}'
    ),
    (
            {'id': 1, 'name': ''},
            '{"message": {"name": ["min length is 1"]}}'
    ),
    (
            {'id': 0, 'name': 'dog'},
            '{"message": {"id": ["min value is 1"]}}'
    ),
    (
            {'name': 'dog'},
            '{"message": {"id": ["required field"]}}'
    ),
    (
            {'id': 'str_val', 'name': 'dog'},
            '{"message": {"id": ["must be of integer type"]}}'
    ),
    (
            {'id': 1, 'name': '123456789012345678901234567890123456789012345678901'},
            '{"message": {"name": ["max length is 50"]}}'
    ),
    (
            {'id': 1, 'name': 'dog', 'tags': [{'id': 1}]},
            '{"message": {"tags": [{"0": [{"name": ["required field"]}]}]}}'
    ),
    (
            {'id': 1, 'name': 'dog', 'tags': [{'id': 1, 'name': ''}]},
            '{"message": {"tags": [{"0": [{"name": ["min length is 1"]}]}]}}'
    ),
    (
            {'id': 1, 'name': 'dog', 'tags': [
                {'id': 1, 'name': '123456789012345678901234567890123456789012345678901'}]
             },
            '{"message": {"tags": [{"0": [{"name": ["max length is 50"]}]}]}}'
    ),
    (
            {'id': 1, 'name': 'dog', 'tags': []},
            '{"message": {"tags": ["min length is 1"]}}'
    ),
    (
            {'id': 1, 'name': 'dog', 'tags': [
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
        'body': JsonUtil.dumps(data)
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.BAD_REQUEST
    assert res['body'] == res_body


@pytest.mark.usefixtures('create_pets_table')
def test_duplicate_id_return_conflict():

    pets_table.put_item(Item={
        'id': 1,
        'name': 'cat'
    })

    event = {
        'body': JsonUtil.dumps({
            'id': 1,
            'name': 'dog',
            'tags': [
                {
                    'id': 1,
                    'name': 'some tag'
                }
            ]
        })
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.CONFLICT
    assert len(pets_table.scan()['Items']) == 1
