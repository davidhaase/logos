from datetime import datetime
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from . import logging
logger = logging.getLogger(__name__)

class DynoDB():
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        self.table = self.dynamodb.Table(table_name)

    def load_items(self, item_list):
        for item in item_list:
            self.table.put_item(Item=item)

    def put_item(self, item):       
        response = self.table.put_item(Item=item)
        return response

    def scan(self):
        response = self.table.scan()
        return response['Items']

        
    def get_distinct(self, column):
        distinct_values = []
        response = self.table.scan()
        for value in response['Items']:
            if value[column] not in distinct_values:
                distinct_values.append(value[column])

        return distinct_values

class Translation(DynoDB):
    def __init__(self, table_name='Translations'):
        super().__init__(table_name=table_name)
        
    def get_translation(self, model_name, input_string):
        logger.info(f'getting translation from inside {__name__}')
        response = self.table.get_item(Key={'model_name': model_name, 'input_string': input_string})
        return response['Item'] if 'Item' in response else False

class Language(DynoDB):
    def __init__(self, table_name='Languages'):
        super().__init__(table_name=table_name)

class Engine(DynoDB):
    def __init__(self, table_name='Engines'):
        super().__init__(table_name=table_name)
    
    def get_engine(self, engine_name):
        response = self.table.get_item(Key={'engine_name': engine_name})
        return response['Item'] if 'Item' in response else False

    def update_engine_code(self, engine_name, engine_code):
        response = self.table.update_item(
            Key={'engine_name': engine_name},
            UpdateExpression="set engine_code=:ec",
            ExpressionAttributeValues={':ec': engine_code},
            ReturnValues="UPDATED_NEW"
        )
        return response

class Model(DynoDB):
    def __init__(self, table_name='Models'):
        super().__init__(table_name=table_name)

    def get_model(self, model_name):
        response = self.table.get_item(Key={'model_name': model_name})
        return response['Item'] if 'Item' in response else False


class CMS(DynoDB):
    def __init__(self, table_name='CMS'):
        super().__init__(table_name=table_name)

    def get_content_by_language(self, language, html_page):
        try:
            response = self.table.get_item(Key={'language': language, 'html_page': html_page})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']




    # def update_movie(self, title, year, rating, plot, actors, dynamodb=None):
    #     if not dynamodb:
    #         dynamodb = boto3.resource('dynamodb')

    #     table = dynamodb.Table('Movies')

    #     response = table.update_item(
    #         Key={
    #             'year': year,
    #             'title': title
    #         },
    #         UpdateExpression="set info.rating=:r, info.plot=:p, info.actors=:a",
    #         ExpressionAttributeValues={
    #             ':r': Decimal(rating),
    #             ':p': plot,
    #             ':a': actors
    #         },
    #         ReturnValues="UPDATED_NEW"
    #     )
    #     return response


    # if __name__ == '__main__':
    #     update_response = update_movie(
    #         "The Big New Movie", 2015, 5.5, "Everything happens all at once.",
    #         ["Larry", "Moe", "Curly"])
    #     print("Update movie succeeded:")
    #     pprint(update_response, sort_dicts=False)


    # def get_movie(self, title, year, dynamodb=None):
    #     if not dynamodb:
    #         dynamodb = boto3.resource('dynamodb')

    #     table = dynamodb.Table('Movies')

    #     try:
    #         response = table.get_item(Key={'year': year, 'title': title})
    #     except ClientError as e:
    #         print(e.response['Error']['Message'])
    #     else:
    #         return response['Item']


    # if __name__ == '__main__':
    #     movie = get_movie("The Big New Movie", 2015,)
    #     if movie:
    #         print("Get movie succeeded:")
    #         pprint(movie, sort_dicts=False)

    # def put_movie(self, title, year, plot, rating, dynamodb=None):
    #     if not dynamodb:
    #         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    #     table = dynamodb.Table('Movies')
    #     response = table.put_item(
    #     Item={
    #             'year': year,
    #             'title': title,
    #             'info': {
    #                 'plot': plot,
    #                 'rating': rating
    #             }
    #         }
    #     )
        # return response


    # if __name__ == '__main__':
    #     movie_resp = put_movie("The Big New Movie", 2015,
    #                            "Nothing happens at all.", 0)
    #     print("Put movie succeeded:")
    #     pprint(movie_resp, sort_dicts=False)


# def create_movie_table(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb')

#     table = dynamodb.create_table(
#         TableName='Movies',
#         KeySchema=[
#             {
#                 'AttributeName': 'year',
#                 'KeyType': 'HASH'  # Partition key
#             },
#             {
#                 'AttributeName': 'title',
#                 'KeyType': 'RANGE'  # Sort key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'year',
#                 'AttributeType': 'N'
#             },
#             {
#                 'AttributeName': 'title',
#                 'AttributeType': 'S'
#             },

#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 10,
#             'WriteCapacityUnits': 10
#         }
#     )
#     return table
