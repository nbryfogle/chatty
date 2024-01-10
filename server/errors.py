"""
A collection of errors the app can raise. I do not think these are used anywhere.
"""

class DatabaseError(Exception):
    """
    Exception to be raised when something goes wrong in the database.
    """

class MalformedDataError(DatabaseError):
    """
    Exception to be raised when the data is malformed.
    """
