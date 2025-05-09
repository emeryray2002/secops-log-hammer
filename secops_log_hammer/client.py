"""Chronicle client module for the SecOps Log Hammer package."""

from typing import Dict, Any

from secops_log_hammer.auth import SecOpsAuth


class ChronicleClient:
    """Client for interacting with the Chronicle API.
    
    This class provides methods for interacting with the Chronicle API,
    including constructing the base URL and instance ID based on the
    provided region, project ID, and customer ID.
    """
    
    def __init__(self, customer_id: str, project_id: str, region: str, auth: SecOpsAuth) -> None:
        """Initialize the Chronicle client.
        
        Args:
            customer_id: The Chronicle customer ID.
            project_id: The Google Cloud project ID.
            region: The Chronicle API region (e.g., us, europe, asia-southeast1).
                Use 'staging' for the staging environment.
            auth: The SecOpsAuth instance for authentication.
        """
        self.customer_id = customer_id
        self.project_id = project_id
        self.region = region
        self.auth = auth

        if region.lower() == "staging":
            self.base_url = "https://staging-chronicle.sandbox.googleapis.com/v1alpha"
        elif region.lower() == "dev":
            self.base_url = "https://autopush-chronicle.sandbox.googleapis.com/v1alpha"
        else:
            self.base_url = f"https://{region}-chronicle.googleapis.com/v1alpha"
        
        if region.lower() in ["staging", "dev"]:
            # For staging and dev environments, use "us" as the region in the instance_id
            self.instance_id = f"projects/{project_id}/locations/us/instances/{customer_id}"
        else:
            self.instance_id = f"projects/{project_id}/locations/{region}/instances/{customer_id}"

    @property
    def session(self):
        """Get the authenticated session.
        
        Returns:
            The AuthorizedSession from the auth object.
        """
        return self.auth.session 