import numpy as np
from qm.pb.general_messages_pb2 import Message_LEVEL_ERROR, Message_LEVEL_INFO, Message_LEVEL_WARNING
from qm._logger import logger, INFO, WARN, ERROR


def fix_object_data_type(obj):
    if isinstance(obj, np.floating):
        return obj.item()
    else:
        return obj


_level_map = {
    Message_LEVEL_ERROR: ERROR,
    Message_LEVEL_WARNING: WARN,
    Message_LEVEL_INFO: INFO,
}
