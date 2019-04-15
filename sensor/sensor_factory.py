from sensor.sensor import *

class SensorFactory(object):
    @staticmethod
    def new_sensor(sensor_id, sensor_type, max_value, min_value, unit, location):
        # Walk through all sensor classes 
        sensor_classes = [j for (i,j) in globals().items() if isinstance(j, type) and issubclass(j, Sensor)]
        for sensor_class in sensor_classes :
            if sensor_class.is_sensor(sensor_type):
                return sensor_class(sensor_id, sensor_type, max_value, min_value, unit, location)
        raise NotImplementedError("{} has not been implemented.".format(sensor_type))