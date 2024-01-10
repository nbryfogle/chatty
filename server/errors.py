class DatabaseError(Exception):
    """
    Exception to be raised when something goes wrong in the database.
    """
    pass

class MalformedDataError(DatabaseError):
    """
    Exception to be raised when the data is malformed.
    """
    pass