import unittest
from ddt import ddt, file_data
from sensor.sensor_factory import SensorFactory 

@ddt
class TestSensor(unittest.TestCase):
    def setUp(self):
        self.sensor = SensorFactory.new_sensor('t1', 'n1', 'TemperatureSensor', 50, -20, 'celsius')
    
    @file_data("test_data/test_transform.json")
    def test_transform(self, unit, unit_policy, input_value, expected_value):
        self.sensor.unit = unit
        value = self.sensor.transform(input_value, unit_policy)
        self.assertEqual(value, expected_value)
    
    @file_data("test_data/test_validate_content.json")
    def test_validate_content(self, item, expected_result):
        result = self.sensor.validate_content(item)
        self.assertEqual(result, expected_result)