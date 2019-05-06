import json
import boto3
import logging
from datetime import datetime
from data_store.data_store_factory import DataStoreFactory
from settings import ENGINE_ADDRESS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

__name__ = "InferenceModule"


def lambda_handler(event, context):

    context_instance, preferences = {}, {}

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    data_store = DataStoreFactory.new_data_store(
        "dynamodb", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    )

    for record in event["Records"]:
        logger.info("Processing event record...")
        try:
            context_instance = data_store.process_event_record(record)
        except Exception as e:
            logger.error(
                "The following exception occured while processing the event record: "
                + str(e)
            )

        logger.info("Updating active users in the database...")
        try:
            manage_users(context_instance, data_store)
            logger.info("Active users successfully updated!")
        except Exception as e:
            logger.error(
                "The following exception occured while updating active users: " + str(e)
            )
            logger.info("Skipping this event...")
            continue

        logger.info("Getting the current preferences from the database...")
        try:
            preferences = get_current_preferences(context_instance, data_store)
        except Exception as e:
            logger.error(
                "The following exception occured while getting the current preferences: "
                + str(e)
            )
            logger.info("Skipping this event...")
            continue

        if preferences:
            try:
                logger.info("Running inference engine with the current preferences...")
                inferred_data = [{
                    "temperature": int(preferences["Temperature"]),
                    "light": preferences["Light"].lower(),
                    "drape": preferences["Drape"].lower(),
                }]
                logger.info("Inference engine run successfully!")
            except Exception as e:
                logger.error(
                    "The following exception occured while running the inference engine: "
                    + str(e)
                )
                logger.info("Skipping this event...")
                continue

            logger.info("Sending the inference results to the adaptation component...")
            try:
                session = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                lambda_client = session.client("lambda", "us-east-1")
                lambda_client.invoke(
                    FunctionName="ReactionModule",
                    InvocationType="Event",
                    Payload=json.dumps(inferred_data),
                )
                logger.info("Inference results sent successfully!")
            except Exception as e:
                logger.error(
                    "The following exception occured while sending the results to the adaptation component: "
                    + str(e)
                )
                logger.info("Skipping this event...")
                continue


def manage_users(item, data_store):

    if "EntryTime" in item.keys():
        to_store = {"UserID": int(item["UserID"]), "Timestamp": item["EntryTime"]}
        data_store.put([to_store], "ActiveUsers")
    elif "ExitTime" in item.keys():
        delete_filter = {"UserID": int(item["UserID"])}
        data_store.delete(delete_filter, "ActiveUsers")


def get_current_preferences(item, data_store):
    active_users = data_store.get_many({}, "ActiveUsers")
    user_ids = [int(u["UserID"]) for u in active_users]

    user_filter = {
        "UserID": {"AttributeValueList": user_ids, "ComparisonOperator": "IN"}
    }

    users = []
    try:
        users = data_store.get_many(user_filter, "Users")
    except Exception as e:
        print(e)
        pass

    max_scl = max(u["SCL"] for u in users)
    high_users = []
    for user in users:
        if user["SCL"] == max_scl:
            for active_user in active_users:
                if active_user["UserID"] == user["UserID"]:
                    user["Timestamp"] = active_user["Timestamp"]
            high_users.append(user)

    top_user = {}
    if len(high_users) > 0:
        top_user = sorted(high_users, key=lambda k: k["Timestamp"], reverse=False)[0]
    if top_user:
        preference_filter = {"UserID": top_user["UserID"], "RoomID": item["RoomID"]}
        return data_store.get(preference_filter, "Preferences")
    return {}


if __name__ == "InferenceModule":
    import sys

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = {
        "Records": [
            {
                "eventID": "11e7236a41d86161782e45c49a88f407",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1553375417,
                    "Keys": {"Timestamp": {"S": now}},
                    "NewImage": {
                        "ExitTime": {"S": now},
                        "UserID": {"S": "3"},
                        "Timestamp": {"S": now},
                        "RoomID": {"S": "R1"},
                    },
                    "SequenceNumber": "978794700000000009513538367",
                    "SizeBytes": 102,
                    "StreamViewType": "NEW_AND_OLD_IMAGES",
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-1:465334783815:table/Context/stream/2018-09-01T15:08:42.064",
            }
        ]
    }
    sys.exit(lambda_handler(event, ""))
