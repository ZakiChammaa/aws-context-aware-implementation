import json
import boto3
import logging
import requests
from datetime import datetime
from data_store.data_store_factory import DataStoreFactory
from settings import ENGINE_ADDRESS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

__name__ = "InferenceModule"

def lambda_handler(event, context):

    context_instance, preferences = {}, {}

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    data_store = DataStoreFactory.new_data_store('dynamodb', AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    for record in event['Records']:
        logger.info("Processing event record...")
        try:
            context_instance = data_store.process_event_record(record)
        except Exception as e:
            logger.error("The following exception occured while processing the event record: " + str(e))

        if context_instance and int(context_instance["Value"]) == 1:

            logger.info("Updating active users in the database...")
            try:
                manage_users(context_instance, data_store)
                logger.info("Active users successfully updated!")
            except Exception as e:
                logger.error("The following exception occured while updating active users: " + str(e))
                logger.info("Skipping this event...")
                continue
            
            logger.info("Getting the current preferences from the database...")
            try:
                preferences = get_current_preferences(context_instance, data_store)
            except Exception as e:
                logger.error("The following exception occured while getting the current preferences: " + str(e))
                logger.info("Skipping this event...")
                continue
            
            if preferences:
                result = []
                try:
                    logger.info("Running Contelog with the current preferences...")
                    payload = {
                        'temperature': preferences["Temperature"],
                        'light': preferences["Light"].lower(),
                        'drape': preferences["Drape"].lower()
                    }
                    result = run(ENGINE_ADDRESS, payload)
                    logger.info("Contelog run successfully!")
                except Exception as e:
                    logger.error("The following exception occured while running Contelog: " + str(e))
                    logger.info("Skipping this event...")
                    continue
                
                logger.info("Sending the inference results to the adaptation component...")
                try:
                    session = boto3.Session(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    lambda_client = session.client('lambda', 'us-east-1')
                    lambda_client.invoke(
                        FunctionName="ReactionModule",
                        InvocationType='Event',
                        Payload=json.dumps(result)
                    )
                    logger.info("Inference results sent successfully!")
                except Exception as e:
                    logger.error("The following exception occured while sending the results to the adaptation component: " + str(e))
                    logger.info("Skipping this event...")
                    continue

def run(engine_address, payload):
    r = requests.get(engine_address, params=payload)
    return json.loads(r.text)

def manage_users(item, data_store):
    
    if "in" in item["SensorType"] and int(item["Value"]) == 1:
        to_store = {
            "UserID": int(item["UserID"]),
            "Timestamp": item["Timestamp"]
        }
        data_store.put([to_store], 'ActiveUsers')
    elif "out" in item["SensorType"] and int(item["Value"]) == 1:
        delete_filter = {
            "UserID": int(item["UserID"])
        }
        data_store.delete(delete_filter, "ActiveUsers")

def get_current_preferences(item, data_store):
    active_users = data_store.get_many({}, 'ActiveUsers')
    user_ids = [int(u["UserID"]) for u in active_users]

    user_filter = {
        'UserID': {
            'AttributeValueList': user_ids,
            'ComparisonOperator': 'IN' 
        }
    }

    users = []
    try:
        users = data_store.get_many(user_filter, 'Users')
    except Exception as e:
        print(e)
        pass
    
    primary, secondary = [], []
    for user in users:
        timestamp = [u["Timestamp"] for u in active_users if u["UserID"] == user["UserID"]][0]
        if user["UserType"] == "Primary":
            primary.append((int(user["UserID"]), datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")))
        elif user["UserType"] == "Secondary":
            secondary.append((int(user["UserID"]), datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")))
    
    user_id = None
    if len(primary) == 1:
        user_id = primary[0][0]
    elif len(primary) > 1:
        primary.sort(key=lambda u:u[1])
        user_id = primary[0][0]
    elif len(primary) == 0:
        if len(secondary) == 1:
            user_id = secondary[0][0]
        elif len(secondary) > 1:
            secondary.sort(key=lambda u:u[1])
            user_id = secondary[0][0]
    if user_id:
        preference_filter = {
            "UserID": user_id,
            "RoomID": item["Location"]
        }
        return data_store.get(preference_filter, "Preferences")
    return {}