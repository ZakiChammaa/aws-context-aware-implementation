import logging
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from data_store.data_store_factory import DataStoreFactory
from actuators.actuators import Actuator

__name__ = "ReactionModule"


def lambda_handler(event, context):
    data_store = DataStoreFactory.new_data_store(
        "dynamodb", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    )

    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    for preferences in event:
        logger.info("Processing inferred data...")
        for preference, value in preferences.items():
            actuator_obj = Actuator()

            logger.info(f"Loading {preference} actuator information in room R1...")
            actuator_info = {}
            try:
                actuator_info = actuator_obj.load_actuator_info(
                    data_store, value, "R1"
                )[0]
            except Exception as e:
                logger.error(
                    f"The following exception occured while loading the {preference} actuator information in room R1: "
                    + str(e)
                )

            current_state = actuator_info["CurrentState"]
            actuator_id = actuator_info["ActuatorID"]
            if current_state != value:
                logger.info(f"Updating actuator {actuator_id} with value {value}...")
                try:
                    actuator_obj.connect(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    actuator_obj.send_command(actuator_id, actuator_info["Command"])
                    data_store.update(
                        "ActuatorID", actuator_id, "CurrentState", value, "Actuators"
                    )
                except Exception as e:
                    logger.error(
                        f"The following exception occured while sending the command to actuator {actuator_id}: "
                        + str(e)
                    )
            else:
                logger.info(f"Actuator {actuator_id} does not need to be updated.")


if __name__ == "ReactionModule":
    import sys

    event = [{"temperature": 20, "light": "low", "drape": "middle"}]
    sys.exit(lambda_handler(event, ""))
