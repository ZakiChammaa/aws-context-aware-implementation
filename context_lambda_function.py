import sys
from context.context import Context
from datetime import datetime
import json
import logging
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, POLICIES_LOCATION
from data_store.data_store_factory import DataStoreFactory

__name__ = "ContextModule"


def lambda_handler(event, context):

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    retention_policies = []
    logger.info("Getting context retention policies...")
    try:
        retention_policies = get_context_policies(
            POLICIES_LOCATION, policy_type="retention"
        )
        logger.info("Context retention policies loaded successfully!")
    except Exception as e:
        logger.error(
            "The following exception occured while loading the context policies: "
            + str(e)
        )

    for record in event["Records"]:
        data_store = DataStoreFactory.new_data_store(
            "dynamodb", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        )

        logger.info("Processing event record...")
        try:
            sensor_reading = data_store.process_event_record(record)
            logger.info("Event processed successfully!")
        except Exception as e:
            logger.error(
                "The following exception occured while processing the event: " + str(e)
            )
            logger.info("Skipping this event...")
            continue

        context_obj = Context(sensor_reading)

        logger.info("Validating sensor reading using retention policies...")
        if context_obj.validate_sensor_reading_ttl(retention_policies):
            logger.info("Sensor reading has been validated!")
            logger.info("Building context instance...")

            try:
                context_instance = context_obj.build_context()
            except Exception as e:
                logger.error(
                    "The following exception occured when attempting to build context: "
                    + str(e)
                )
                logger.info("Skipping this event...")
                continue

            logger.info("Context built successfully!")
            logger.info(
                "Storing the context instance in the Context table in DynamoDB..."
            )

            try:
                data_store.put([context_instance], "Context")
            except Exception as e:
                logger.error(
                    "The following exception occured when attempting to store the context instance: "
                    + str(e)
                )
                logger.info("Skipping this event...")
                continue

            logger.info("Context instance stored successfully!")
        else:
            logger.info("Sensor reading is too old. Skipping...")
            continue
    logger.info("Done processing current events.")


def get_context_policies(policies_location, policy_type=None):
    policies = []
    with open(policies_location) as f:
        policies = json.load(f)

    if policy_type:
        return [p for p in policies if p["type"] == policy_type]
    return policies


if __name__ == "ContextModule":
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = {
        "Records": [
            {
                "eventID": "46ed79fd157acd5b205cea09b28216d9",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1535301720,
                    "Keys": {"SensorID": {"S": "ecr_out1"}, "Timestamp": {"S": now}},
                    "NewImage": {
                        "SensorID": {"S": "ecr_out1"},
                        "Value": {"N": "1"},
                        "Timestamp": {"S": now},
                        "SensorType": {"S": "door"},
                        "RoomID": {"S": "R1"},
                    },
                    "SequenceNumber": "74807100000000013576980822",
                    "SizeBytes": 107,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-1:465334783815:table/temperature/stream/2018-08-10T23:36:48.420",
            }
        ]
    }
    sys.exit(lambda_handler(event, ""))
