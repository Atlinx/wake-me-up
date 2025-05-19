from enum import IntEnum


class MsgID(IntEnum):
    # Server -> Client
    RESULT = (0,)  # Result of executing a command

    # Client -> Server
    AUTH = (128,)  # Authenticates using a password
    WAKEUP = (129,)  # Requests a wakeup
    LIST = (130,)  # Lists available computers to wake up


def to_dict(obj):
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(elem) for elem in obj]
    elif hasattr(obj, "__dict__"):
        return to_dict(obj.__dict__)
    else:
        return obj
