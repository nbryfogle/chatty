class CommandError(Exception):
    """
    Exception to be raised when a command fails.
    """
    pass


class CommandNotFound(CommandError):
    """
    Exception to be raised when a command is not found.
    """
    pass


class SocketError(Exception):
    """
    Exception to be raised when a socket fails.
    """
    pass


class InsufficientPermissions(Exception):
    """
    Exception to be raised when a user has insufficient permissions.
    """
    pass