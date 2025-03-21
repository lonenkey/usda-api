class USDAAPIError(Exception):
    """Base exception for USDA API errors"""
    pass

class CredentialsError(Exception):
    """Exception for credential related errors"""
    pass

class InputError(Exception):
    """Exception for user input errors"""
    pass