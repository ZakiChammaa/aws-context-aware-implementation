from data_store.data_store import *


class DataStoreFactory(object):
    @staticmethod
    def new_data_store(data_store, access_key_id, secret_access_key):
        # Walk through all information_loader classes
        data_store_classes = [
            j
            for (i, j) in globals().items()
            if isinstance(j, type) and issubclass(j, DataStore)
        ]
        for data_store_class in data_store_classes:
            if data_store_class.is_data_store(data_store):
                return data_store_class(
                    access_key_id=access_key_id, secret_access_key=secret_access_key
                )
        raise NotImplementedError("{} has not been implemented.".format(data_store))
