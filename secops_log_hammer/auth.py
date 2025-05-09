"""Authentication module for the SecOps Log Hammer package."""

from typing import Optional, List

from secops_log_hammer.exceptions import AuthenticationError

# Chronicle API scopes
CHRONICLE_SCOPES: List[str] = ["https://www.googleapis.com/auth/cloud-platform"]


class SecOpsAuth:
    """Authentication handler for Chronicle API.
    
    This class handles authentication with the Chronicle API using
    either a service account key file or Application Default Credentials.
    """
    
    def __init__(self, service_account_path: Optional[str] = None) -> None:
        """Initialize the authentication handler.
        
        Args:
            service_account_path: Optional path to a service account key file.
                If not provided, Application Default Credentials will be used.
        """
        self.service_account_path = service_account_path
        self.credentials = self._get_credentials()
        self._session = None

    def _get_credentials(self):
        """Get Google Cloud credentials.
        
        Returns:
            The Google Cloud credentials object.
            
        Raises:
            AuthenticationError: If credentials cannot be obtained.
        """
        try:
            if self.service_account_path:
                from google.oauth2 import service_account
                return service_account.Credentials.from_service_account_file(
                    self.service_account_path, scopes=CHRONICLE_SCOPES
                )
            else:
                import google.auth
                credentials, _ = google.auth.default(scopes=CHRONICLE_SCOPES)
                return credentials
        except Exception as e:
            raise AuthenticationError(f"Failed to get credentials: {str(e)}")

    @property
    def session(self):
        """Get an authenticated session.
        
        Returns:
            An AuthorizedSession object that can be used for API requests.
        """
        if self._session is None:
            import google.auth.transport.requests
            self._session = google.auth.transport.requests.AuthorizedSession(
                self.credentials
            )
        return self._session 