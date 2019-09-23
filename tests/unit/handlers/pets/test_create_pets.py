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
