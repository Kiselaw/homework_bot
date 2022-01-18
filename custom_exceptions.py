class FailedRequestError(Exception):
    pass


class EmptyError(Exception):
    pass


class Not200Error(Exception):
    pass


class NoKeyError(Exception):
    pass


class WrongDataTypeError(Exception):
    pass


class MessageSendingError(Exception):
    pass


class FailedJSONError(Exception):
    pass
