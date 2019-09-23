import json
import os

import boto3
import pytest

from handlers.pets.create import handler

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


@pytest.mark.usefixtures('create_pets_table')
def test_valid_data_will_creates_pet():

    event = {
        'body': json.dumps({
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
    assert res['statusCode'] == 201
    data = json.loads(res['body'])
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

])
def test_invalid_json_will_return_bad_request(data, res_body):

    event = {
        'body': json.dumps(data)
    }

    res = handler(event, {})
    assert res['statusCode'] == 400
    assert res['body'] == res_body
