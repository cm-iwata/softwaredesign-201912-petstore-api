import os

import boto3
import moto
import pytest


os.environ['PETS_TABLE'] = 'pets'


@pytest.fixture(autouse=True)
def start_moto_mock():

    moto.mock_dynamodb2().start()


@pytest.fixture
def create_pets_table():

    region = os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-1')
    dynamo = boto3.client('dynamodb', region_name=region)

    dynamo.create_table(
      TableName=os.environ['PETS_TABLE'],
      KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
      ],
      AttributeDefinitions=[
            {
              'AttributeName': 'id',
              'AttributeType': 'N'
            }
      ]
    )
