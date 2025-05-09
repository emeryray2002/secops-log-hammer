"""Log ingestion module for the SecOps Log Hammer package."""

import base64
import sys
import time
from typing import Dict, Any, List, Tuple, Optional

import requests

from secops_log_hammer.client import ChronicleClient
from secops_log_hammer.exceptions import APIError


def create_forwarder(client: ChronicleClient, display_name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new forwarder in Chronicle.
    
    Args:
        client: The ChronicleClient instance.
        display_name: The display name for the forwarder.
        metadata: Optional forwarder metadata (asset_namespace, labels).
        
    Returns:
        The response from the API containing the forwarder details.
        
    Raises:
        APIError: If the API request fails.
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders"
    
    # Ensure we have a metadata object
    if metadata is None:
        metadata = {}
    
    # Create the payload with the proper structure
    payload = {
        "displayName": display_name, 
        "config": {
            "uploadCompression": False,
            "metadata": metadata,
            "serverSettings": {
                "enabled": False,
                "httpSettings": {
                    "routeSettings": {}
                }
            }
        }
    }
    
    try:
        response = client.session.post(url, json=payload)
        if response.status_code != 200:
            raise APIError(f"Failed to create forwarder '{display_name}': {response.text}", response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to create forwarder '{display_name}': {str(e)}")


def list_forwarders(client: ChronicleClient) -> List[Dict[str, Any]]:
    """List all forwarders in Chronicle.
    
    Args:
        client: The ChronicleClient instance.
        
    Returns:
        A list of forwarders.
        
    Raises:
        APIError: If the API request fails.
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders"
    all_forwarders = []
    page_token = None
    try:
        while True:
            params = {"pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            response = client.session.get(url, params=params)
            if response.status_code != 200:
                raise APIError(f"Failed to list forwarders: {response.text}", response.status_code)
            
            data = response.json()
            all_forwarders.extend(data.get("forwarders", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        return all_forwarders
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to list forwarders: {str(e)}")


def get_or_create_forwarder(client: ChronicleClient, display_name: str = "PythonLogIngestScriptForwarder", namespace: Optional[str] = None) -> str:
    """Get or create a forwarder in Chronicle.
    
    Args:
        client: The ChronicleClient instance.
        display_name: The display name for the forwarder.
        namespace: Optional namespace to include in the forwarder metadata.
        
    Returns:
        The forwarder ID.
        
    Raises:
        APIError: If the API request fails.
        SystemExit: If there's a permissions issue.
    """
    try:
        forwarders = list_forwarders(client)
        for f in forwarders:
            if f.get("displayName") == display_name:
                # Extract only the ID part of the name
                return f.get("name", "").split("/")[-1]
        
        # If not found, create a forwarder with proper metadata
        metadata = {}
        if namespace:
            metadata["asset_namespace"] = namespace
            
        created_forwarder = create_forwarder(client, display_name, metadata)
        return created_forwarder.get("name", "").split("/")[-1]
    except APIError as e:
        print(f"Error managing forwarder: {e}. Ensure the service account has 'Chronicle API Editor' or 'Chronicle API Admin' role.", file=sys.stderr)
        sys.exit(1)


def extract_forwarder_id(forwarder_id: str, client: ChronicleClient) -> str:
    """Extract the forwarder resource name from an ID.
    
    Args:
        forwarder_id: The forwarder ID or resource name.
        client: The ChronicleClient instance.
        
    Returns:
        The full forwarder resource name.
    """
    # If it already has slashes, assume it's a resource name
    if '/' in forwarder_id:
        return forwarder_id
    
    # Otherwise, construct the resource name
    return f"{client.instance_id}/forwarders/{forwarder_id}"


def ingest_logs(
    client: ChronicleClient, 
    log_type: str, 
    logs: List[Dict[str, Any]], 
    forwarder_id: str,
    namespace: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None
) -> Tuple[int, int]:
    """Ingest logs into Chronicle.
    
    Args:
        client: The ChronicleClient instance.
        log_type: The type of logs to ingest (e.g., WINEVTLOG, OKTA).
        logs: A list of log data dictionaries.
        forwarder_id: The ID of the forwarder to use.
        namespace: Optional asset namespace for the logs (sets on forwarder metadata, not on log entries).
        labels: Optional labels to attach to the logs.
        
    Returns:
        A tuple of (number of logs sent, total bytes sent).
        
    Raises:
        APIError: If the API request fails.
        ValueError: If the log data is invalid.
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/logs:import"
    
    # Use the full resource name for the forwarder
    forwarder_resource_name = extract_forwarder_id(forwarder_id, client)

    entries = []
    total_bytes = 0
    for log_data_dict in logs:
        # The log_data_dict should already contain the "data" field as a JSON string
        # and other fields like "log_entry_time", "collection_time".
        
        # Ensure 'data' field is a string, then encode to base64
        if not isinstance(log_data_dict.get("data"), str):
            raise ValueError("Log 'data' field must be a string for base64 encoding.")

        raw_log_str = log_data_dict["data"]
        encoded_log_data = base64.b64encode(raw_log_str.encode('utf-8')).decode('utf-8')
        total_bytes += len(raw_log_str.encode('utf-8'))

        entry = {
            "data": encoded_log_data,
            "log_entry_time": log_data_dict["log_entry_time"],
            "collection_time": log_data_dict["collection_time"]
        }
            
        # Add labels if provided - convert to the expected format
        if labels:
            entry["labels"] = {key: {"value": value} for key, value in labels.items()}
            
        entries.append(entry)

    payload = {
        "inline_source": {
            "logs": entries,
            "forwarder": forwarder_resource_name
        }
    }

    max_retries = 5
    backoff_factor = 2 
    for attempt in range(max_retries):
        try:
            response = client.session.post(url, json=payload)
            
            # Check for errors and provide detailed error messages
            if response.status_code != 200:
                if response.status_code == 403:
                    error_msg = f"Permission denied (403): {response.text}. Ensure the service account has permissions for log type '{log_type}'."
                    
                    # For GCP logs, provide more specific guidance
                    if log_type.startswith("GCP_"):
                        error_msg += f" For GCP logs, check if this requires a specific forwarder setup or labels."
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                
                if attempt < max_retries - 1:
                    print(f"{error_msg} Retrying in {backoff_factor * (2 ** attempt)} seconds...", file=sys.stderr)
                    time.sleep(backoff_factor * (2 ** attempt))
                    continue
                else:
                    raise APIError(error_msg, response.status_code)
            
            # For successful ingestion, Chronicle API often returns an empty JSON {} or a specific operation ID
            return len(logs), total_bytes 
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                sleep_time = backoff_factor * (2 ** attempt)
                print(f"Request exception: {e}. Retrying in {sleep_time} seconds...", file=sys.stderr)
                time.sleep(sleep_time)
                continue
            else:
                raise APIError(f"Failed to ingest logs after {max_retries} retries: {str(e)}")
    
    # This should not be reached if retries are handled correctly
    return 0, 0 