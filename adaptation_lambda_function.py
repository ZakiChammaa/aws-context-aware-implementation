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
        for _, value in preferences.items():
            actuator_obj = Actuator()

            logger.info("Loading actuator information...")
            actuator_info = {}
            try:
                actuator_info = actuator_obj.load_actuator_info(
                    data_store, value, "R1"
                )[0]
            except Exception as e:
                logger.error(
                    "The following exception occured while loading the actuator information: "
                    + str(e)
                )

            current_state = actuator_info["CurrentState"]
            if current_state != value:
                logger.info("Sending command to actuator...")
                try:
                    actuator_id = actuator_info["ActuatorID"]
                    actuator_obj.connect(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    actuator_obj.send_command(actuator_id, actuator_info["Command"])
                    data_store.update(
                        "ActuatorID", actuator_id, "CurrentState", value, "Actuators"
                    )
                except Exception as e:
                    logger.error(
                        "The following exception occured while sending the command to the actuator: "
                        + str(e)
                    )
            else:
                logger.info("Actuator does not need to be updated.")


if __name__ == "ReactionModule":
    import sys

    event = [{"temperature": 20, "light": "low", "drape": "middle"}]
    sys.exit(lambda_handler(event, ""))
