from abc import ABC, abstractmethod


class Sensor(ABC):
    def __init__(self, sensor_id, sensor_type, max_value, min_value, unit, location):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.max_value = max_value
        self.min_value = min_value
        self.unit = unit
        self.location = location

    @staticmethod
    def is_sensor(sensor_type):
        return False

    @abstractmethod
    def transform(self, item, unit_policy):
        pass

    def validate_content(self, item):
        if item["Value"] >= self.min_value and item["Value"] <= self.max_value:
            return True
        return False


class TemperatureSensor(Sensor):
    @staticmethod
    def is_sensor(sensor_type):
        return sensor_type.lower() == "temperature"

    def transform(self, item, unit_policy):
        if self.unit != unit_policy:
            if unit_policy.lower() == "fahrenheit":
                item["Value"] = (item["Value"] * 1.8) + 32
            elif unit_policy.lower() == "celsius":
                item["Value"] = (item["Value"] - 32) * (5 / 9)
        item["RoomID"] = self.location
        item["SensorType"] = self.sensor_type


class HumiditySensor(Sensor):
    @staticmethod
    def is_sensor(sensor_type):
        return sensor_type.lower() == "humidity"

    def transform(self, item, unit_policy):
        item["RoomID"] = self.location
        item["SensorType"] = self.sensor_type


class DoorSensor(Sensor):
    @staticmethod
    def is_sensor(sensor_type):
        return sensor_type.lower() == "door"

    def transform(self, item, unit_policy):
        item["RoomID"] = self.location
        item["SensorType"] = self.sensor_type

