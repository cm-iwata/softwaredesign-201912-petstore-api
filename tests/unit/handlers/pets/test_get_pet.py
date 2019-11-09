from http import HTTPStatus
import os

import boto3
import pytest

from handlers.pets.get import handler
from src.utils.json_util import JsonUtil

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


@pytest.mark.usefixtures('create_pets_table')
def test_non_exists_id_will_return_not_found():

    event = {
        'pathParameters': {
            'petId': '1'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('create_pets_table')
def test_exists_id_will_return_pet_info():

    event = {
        'pathParameters': {
            'petId': '1'
        }
    }

    pets_table.put_item(Item={
        'id': 1,
        'name': 'dog',
        'tags': [
            {
                'id': 1,
                'name': 'some tag'
            }
        ]
    })

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.OK
    pet = JsonUtil.loads(res['body'])
    assert pet['id'] == 1
    assert pet['name'] == 'dog'
    assert pet['tags'][0]['id'] == 1
    assert pet['tags'][0]['name'] == 'some tag'


@pytest.mark.usefixtures('create_pets_table')
def test_invalid_pet_id_will_return_not_found():

    event = {
        'pathParameters': {
            'petId': 'str val'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NOT_FOUND
