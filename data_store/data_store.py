import boto3
from abc import ABC, abstractmethod

class DataStore(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass
    
    @staticmethod
    def is_data_store(data_store):
        return False

    @abstractmethod
    def get(self, filter, table):
        pass
    
    @abstractmethod
    def get_many(self, filter, table):
        pass

    @abstractmethod
    def put(self, items, table):
        pass
    
    @abstractmethod
    def process_event_record(self, record):
        pass
    
    def validate_output_format(self, item):
        return True

class DynamoDB(DataStore):
    def __init__(self, **kwargs):
        self.session = None
        if all (k in kwargs for k in ("access_key_id", "secret_access_key")):
            access_key_id = kwargs['access_key_id']
            secret_access_key = kwargs['secret_access_key']

            self.session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key
            )
        else:
            self.session = boto3.Session()

    @staticmethod
    def is_data_store(data_store):
        return data_store == 'dynamodb'
        
    def get(self, filter, table):
        dynamodb = self.session.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table(table)

        data = table.get_item(
            Key=filter
        )
        return data['Item']
    
    def get_many(self, filter, table):
        dynamodb = self.session.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table(table)

        response = table.scan(
            ScanFilter=filter
        )
        return response['Items']
    
    def put(self, items, table):
        dynamodb = self.session.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table(table)

        for item in items:
            if 'flag' in item.keys():
                continue
            elif self.validate_output_format(item):
                table.put_item(Item=item)
            else:
                raise('Invalid sensor data format\n')
    
    def update(self, key_id, key_value, field, new_val, table):
        dynamodb = self.session.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table(table)
        
        update_expression = "SET {} = :value".format(field)
        table.update_item(
            Key={
                key_id: key_value
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues={
                ':value': new_val,
            }
        )
    
    def delete(self, filter, table):
        dynamodb = self.session.resource('dynamodb', 'us-east-1')
        table = dynamodb.Table(table)

        table.delete_item(
            Key=filter
        )

    def process_event_record(self, record):
        data = {}
        raw_data = record['dynamodb']['NewImage']

        for item in raw_data:
            for _, v in raw_data[item].items():
                data[item] = v
        return data