from http import HTTPStatus
import os

import boto3
import pytest

from handlers.pets.delete import handler

dynamodb = boto3.resource('dynamodb')
pets_table = dynamodb.Table(os.environ['PETS_TABLE'])


# TODO moto1.3.13時点で条件付き削除が正しく動作しないためコメントアウト
# https://github.com/spulec/moto/issues/2410
# @pytest.mark.usefixtures('create_pets_table')
# def test_non_exists_id_will_return_not_found():
#
#     event = {
#         'pathParameters': {
#             'petId': '1'
#         }
#     }
#
#     res = handler(event, {})
#     assert res['statusCode'] == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('create_pets_table')
def test_exists_id_will_return_no_content():

    event = {
        'pathParameters': {
            'petId': '1'
        }
    }

    pets_table.put_item(Item={
        'id': 1,
        'name': 'dog'
    })

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NO_CONTENT


@pytest.mark.usefixtures('create_pets_table')
def test_invalid_pet_id_will_return_not_found():

    event = {
        'pathParameters': {
            'petId': 'str val'
        }
    }

    res = handler(event, {})
    assert res['statusCode'] == HTTPStatus.NOT_FOUND
