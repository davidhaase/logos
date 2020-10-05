from datetime import datetime
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import pprint


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
        
    def get_item(self, model_name):
        try:
            response = self.table.get_item(Key={'engine':'devX', 'model_name':model_name})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

        
    def get_distinct(self, column):
        distinct_values = []
        response = self.table.scan()
        for value in response['Items']:
            if value[column] not in distinct_values:
                distinct_values.append(value[column])

        return distinct_values

class dynoTranslation(DynoDB):
    def __init__(self, table_name='Translations'):
        super().__init__(table_name=table_name)
        
    def query_translations(self, model_name):       
        response = self.table.query(
            KeyConditionExpression=Key('model_name').eq(model_name)
        )
        return response['Items']

class DynoLanguage(DynoDB):
    def __init__(self, table_name='Languages'):
        super().__init__(table_name=table_name)

class DynoModel(DynoDB):
    def __init__(self, table_name='Models'):
        super().__init__(table_name=table_name)




        
    

    # if __name__ == '__main__':
    #     query_year = 1985
    #     print(f"Movies from {query_year}")
    #     movies = query_movies(query_year)
    #     for movie in movies:
    #         print(movie['year'], ":", movie['title'])

    def update_movie(title, year, rating, plot, actors, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table('Movies')

        response = table.update_item(
            Key={
                'year': year,
                'title': title
            },
            UpdateExpression="set info.rating=:r, info.plot=:p, info.actors=:a",
            ExpressionAttributeValues={
                ':r': Decimal(rating),
                ':p': plot,
                ':a': actors
            },
            ReturnValues="UPDATED_NEW"
        )
        return response


    # if __name__ == '__main__':
    #     update_response = update_movie(
    #         "The Big New Movie", 2015, 5.5, "Everything happens all at once.",
    #         ["Larry", "Moe", "Curly"])
    #     print("Update movie succeeded:")
    #     pprint(update_response, sort_dicts=False)


    def get_movie(title, year, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb')

        table = dynamodb.Table('Movies')

        try:
            response = table.get_item(Key={'year': year, 'title': title})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']


    # if __name__ == '__main__':
    #     movie = get_movie("The Big New Movie", 2015,)
    #     if movie:
    #         print("Get movie succeeded:")
    #         pprint(movie, sort_dicts=False)

    def put_movie(title, year, plot, rating, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        table = dynamodb.Table('Movies')
        response = table.put_item(
        Item={
                'year': year,
                'title': title,
                'info': {
                    'plot': plot,
                    'rating': rating
                }
            }
        )
        return response


    # if __name__ == '__main__':
    #     movie_resp = put_movie("The Big New Movie", 2015,
    #                            "Nothing happens at all.", 0)
    #     print("Put movie succeeded:")
    #     pprint(movie_resp, sort_dicts=False)


def create_movie_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='Movies',
        KeySchema=[
            {
                'AttributeName': 'year',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'title',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'year',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

# if __name__ == '__main__':
#     movie_table = create_movie_table()
#     print("Table status:", movie_table.table_status)
# def query_translations(modelName, dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb')

#     table = dynamodb.Table('Translations')
#     response = table.query(
#         KeyConditionExpression=Key('modelName').eq(modelName)
#     )
#     return response['Items']
### To load look-up tables
# (venv) $ flask shell
# >>> from logos import db
# >>> from app import data_loader as ld
# >>> ld.load_data(db, Language, TranslationModel)
# '1 français'
# '2 english'
# '3 español'
# '4 türkçe'
# '5 italiano'
# '6 deutsch'


# class Translation(db.Model):
#     __tablename__ = 'translations'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime())
#     source_txt = db.Column(db.String(64), index=True)
#     target_txt = db.Column(db.String(64), index=True)
#     model_id = db.Column(db.Integer)
#     elapsed_time = db.Column(db.String(64))

#     def __repr__(self):
#         return '<Translation %r>' % self.input

# class TranslationModel(db.Model):
#     __tablename__ = 'translation_models'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime())
#     name = db.Column(db.String(64))
#     summary = db.Column(db.String(64))
#     number_of_epochs = db.Column(db.Integer, db.ForeignKey('epochs.id'))
#     number_of_sentences = db.Column(db.Integer, db.ForeignKey('subsets.id'))
#     source_lang_id = db.Column(db.Integer)
#     target_lang_id = db.Column(db.Integer)
#     build_id = db.Column(db.Integer)
#     model_path = db.Column(db.String)
#     source_tokenizer = db.Column(db.String)
#     source_max_length = db.Column(db.Integer)
#     source_word_count = db.Column(db.Integer)
#     target_tokenizer = db.Column(db.String)
#     target_word_count = db.Column(db.Integer)
#     target_max_length = db.Column(db.Integer)
#     aws_bucket_name = db.Column(db.String(64))

#     def __repr__(self):
#         return '<TranslationModel %r>' % self.name

# class Build(db.Model):
#     __tablename__ = 'builds'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     summary = db.Column(db.String(64))

#     def __repr__(self):
#         return '<Build %r>' % self.number_of_sentences


# # Look-Up Tables
# class Language(db.Model):
#     __tablename__ = 'languages'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(64), unique=True)
#     name = db.Column(db.String(64))
#     en_name = db.Column (db.String(64))
#     # source_langs = db.relationship('TranslationModel', foreign_keys=[TranslationModel.source_lang_id], lazy='dynamic')
#     # target_langs = db.relationship('TranslationModel', foreign_keys=[TranslationModel.target_lang_id], lazy='dynamic')

#     def __repr__(self):
#         return '<Language %r>' % self.name

# class Epoch(db.Model):
#     __tablename__ = 'epochs'
#     id = db.Column(db.Integer, primary_key=True)
#     number_of_epochs = db.Column(db.Integer, unique=True)

#     def __repr__(self):
#         return '<Epoch %r>' % self.number_of_epochs

# class Subset(db.Model):
#     __tablename__ = 'subsets'
#     id = db.Column(db.Integer, primary_key=True)
#     number_of_sentences = db.Column(db.Integer, unique=True)
#     display_string_of_number = db.Column(db.String(64))

#     def __repr__(self):
#         return '<Subset %r>' % self.number_of_sentences



# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role', lazy='dynamic')
#
#     def __repr__(self):
#         return '<Role %r>' % self.name
#
#
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#
#     def __repr__(self):
#         return '<User %r>' % self.username
