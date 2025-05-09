"""Exception classes for the SecOps Log Hammer package."""

from typing import Optional


class SecOpsError(Exception):
    """Base exception for SecOps SDK.
    
    This serves as the parent class for all exceptions in the SecOps SDK.
    """
    pass


class AuthenticationError(SecOpsError):
    """Raised when authentication fails.
    
    This exception is raised when there's a problem authenticating with 
    the Chronicle API, such as invalid credentials or permission issues.
    """
    pass


class APIError(SecOpsError):
    """Raised when an API request fails.
    
    This exception is raised when an API request to Chronicle fails,
    such as invalid parameters, rate limiting, or server errors.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize the APIError exception.
        
        Args:
            message: The error message.
            status_code: The HTTP status code that triggered the error, if applicable.
        """
        self.status_code = status_code
        super().__init__(message)
    
    def __str__(self) -> str:
        """Return a string representation of the error.
        
        Returns:
            A string with the error message and status code if available.
        """
        if self.status_code:
            return f"API Error (HTTP {self.status_code}): {super().__str__()}"
        return super().__str__() 