from datetime import datetime


class Context:
    def __init__(self, sensor_reading):
        self.sensor_id = sensor_reading["SensorID"]
        self.sensor_type = sensor_reading["SensorType"]
        self.sensor_value = sensor_reading["Value"]
        self.sensor_location = sensor_reading["RoomID"]
        self.sensor_timestamp = sensor_reading["Timestamp"]

    def validate_sensor_reading_ttl(self, retention_policies):
        for policy in retention_policies:
            if (
                self.sensor_type in policy["affected_instances"]
                or "all" in policy["affected_instances"]
            ):

                ttl = policy["body"]["ttl"]
                ttl_value = ttl["value"]
                ttl_unit = ttl["unit"]

                td = datetime.now() - datetime.strptime(
                    self.sensor_timestamp, "%Y-%m-%d %H:%M:%S"
                )
                td_dict = {
                    "days": td.days,
                    "hours": td.seconds // 3600,
                    "minutes": (td.seconds // 60) % 60,
                    "seconds": td.seconds,
                }

                if ttl_unit == "days":
                    if td_dict["days"] > ttl_value:
                        return False
                elif ttl_unit == "hours":
                    if td_dict["days"] > 0 or td_dict["hours"] > ttl_value:
                        return False
                elif ttl_unit == "minutes":
                    if (
                        td_dict["days"] > 0
                        or td_dict["hours"] > 0
                        or td_dict["minutes"] > ttl_value
                    ):
                        return False
                elif ttl_unit == "seconds":
                    if (
                        td_dict["days"] > 0
                        or td_dict["hours"] > 0
                        or td_dict["minutes"] > 0
                        or td_dict["seconds"] > ttl_value
                    ):
                        return False
        return True

    def build_context(self):
        time_key = ""
        if "in" in self.sensor_id.lower():
            time_key = "EntryTime"
        elif "out" in self.sensor_id.lower():
            time_key = "ExitTime"

        return {
            "Timestamp": self.sensor_timestamp,
            time_key: self.sensor_timestamp,
            "RoomID": self.sensor_location,
            "UserID": self.sensor_value,
        }
