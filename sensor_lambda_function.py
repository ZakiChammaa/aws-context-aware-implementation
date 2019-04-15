import sys
import boto3
import logging
from datetime import datetime
from sensor.sensor_factory import SensorFactory
from data_store.data_store_factory import DataStoreFactory
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

__name__ = "IOTListner"

def lambda_handler(event, context):

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    data_store = DataStoreFactory.new_data_store('dynamodb', AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    sensor_id = event['SensorID']

    logger.info("Loading sensor information...")
    sensor_info = data_store.get({'SensorID': sensor_id}, 'Sensors')

    sensor = SensorFactory.new_sensor(
        sensor_info['SensorID'], 
        sensor_info['SensorType'],
        sensor_info['MaxValue'],
        sensor_info['MinValue'],
        sensor_info['Unit'],
        sensor_info['RoomID']
    )

    logger.info("Sensor information loaded successfully!")

    logger.info("Transforming sensor reading...")
    sensor.transform(event, sensor_info['Unit'])
    logger.info("Sensor reading transformed successfully!")

    logger.info("Validating sensor reading...")
    if not sensor.validate_content(event):
        event['flag'] = 'remove'
    logger.info("Validation complete!")

    logger.info("Storing sensor reading in data store...")
    try:
        data_store.put([event], 'SensorReadings')
        logger.info("Sensor reading stored successfully!")
    except Exception as e:
        logger.error("The following exception occured when attempting to store the sensor reading: " + str(e))
        logger.info("Skipping this event...")

if __name__ == "IOTListner":
    event = { 
        'SensorID': 'ecr_in1',
        'Value': 1,
        'UserID': 1,
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    sys.exit(lambda_handler(event, ""))