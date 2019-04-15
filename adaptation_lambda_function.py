import sys
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from data_store.data_store_factory import DataStoreFactory
from actuators.actuators import Actuator

__name__ = "ReactionModule"

def lambda_handler(event, context):
    data_store = DataStoreFactory.new_data_store('dynamodb', AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    actions = [e['action'] for e in event]

    for action in actions:
        actuator_obj = Actuator()
        actuator_info = actuator_obj.load_actuator_info(data_store, action, 'node1')[0]
        current_state = actuator_info["CurrentState"]
        if current_state != action:
            actuator_id = actuator_info["ActuatorID"]
            actuator_obj.connect(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            actuator_obj.send_command(actuator_id, actuator_info["Command"])
            data_store.update("ActuatorID", actuator_id, "CurrentState", action, "Actuators")

if __name__ == "ReactionModule":
    event = [{'action': 't23'}, {'action': 'high'}, {'action': 'down'}]
    sys.exit(lambda_handler(event, ""))