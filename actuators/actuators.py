import json
import boto3

# from abc import ABC, abstractmethod


class Actuator:
    # @staticmethod
    # def is_actuator(actuator_type):
    #     return False

    def load_actuator_info(self, data_store, action, room_id):
        actuator_ids = []
        action_filter = {
            "Action": {"AttributeValueList": [action], "ComparisonOperator": "IN"}
        }

        actions = data_store.get_many(action_filter, "Actions")

        for action in actions:
            if "ActuatorID" in action:
                actuator_ids.append(action["ActuatorID"])

        actuator_filter = {
            "ActuatorID": {
                "AttributeValueList": actuator_ids,
                "ComparisonOperator": "IN",
            },
            "RoomID": {"AttributeValueList": [room_id], "ComparisonOperator": "IN"},
        }

        actuators = data_store.get_many(actuator_filter, "Actuators")

        for actuator in actuators:
            for action in actions:
                if actuator["ActuatorID"] == action["ActuatorID"]:
                    actuator["Command"] = int(action["Command"])

        return actuators

    def connect(self, access_key_id, secret_access_key):
        session = boto3.Session(access_key_id, secret_access_key)
        self.client = session.client("lambda", "us-east-1")

    def send_command(self, actuator_id, command):
        msg = {"command": command}
        self.client.invoke(
            FunctionName=actuator_id, InvocationType="Event", Payload=json.dumps(msg)
        )

    def convert_action_to_command(self, action):
        pass

    def get_actuator_status(self, actuator_id):
        return "ok"


# class Temperature(Actuator):
#     @staticmethod
#     def is_actuator(actuator_type):
#         return actuator_type.lower() == "temperature"

# class Light(Actuator):
#     @staticmethod
#     def is_actuator(actuator_type):
#         return actuator_type.lower() == "light"

# class Drape(Actuator):
#     @staticmethod
#     def is_actuator(actuator_type):
#         return actuator_type.lower() == "drape"
