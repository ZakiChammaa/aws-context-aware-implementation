from actuators.actuators import *

class ActuatorFactory(object):
    @staticmethod
    def new_actuator(action):
        # Walk through all actuator classes 
        actuator_classes = [j for (i,j) in globals().items() if isinstance(j, type) and issubclass(j, Actuator)]
        for actuator_class in actuator_classes :
            if actuator_class.is_actuator(action):
                return actuator_class()
        raise NotImplementedError("{} has not been implemented.".format(action))