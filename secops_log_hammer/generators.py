"""Log generators module for the SecOps Log Hammer package."""

import copy
import json
import random
import string
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def generate_ip_address() -> str:
    """Generate a random IP address.
    
    Returns:
        A random IPv4 address as a string.
    """
    return f"{random.randint(1, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"


def generate_hostname(domains: List[str]) -> str:
    """Generate a random hostname in a given domain.
    
    Args:
        domains: List of domains to choose from.
        
    Returns:
        A random hostname as a string.
    """
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 15)))
    return f"{name}.{random.choice(domains)}"


def generate_username() -> str:
    """Generate a random username.
    
    Returns:
        A random username as a string.
    """
    first_names = ["john", "jane", "alex", "emily", "michael", "sarah", "david", "laura"]
    last_names = ["smith", "jones", "doe", "brown", "wilson", "taylor", "lee", "white"]
    return f"{random.choice(first_names)}{random.choice(last_names)}{random.randint(10,99)}"


def generate_windows_process() -> Dict[str, str]:
    """Generate a random Windows process name and path.
    
    Returns:
        A dictionary containing the process name, command line, and image file name.
    """
    # List of common Windows process names
    process_names = [
        "conhost.exe",        # Console Host
        "svchost.exe",        # Service Host
        "explorer.exe",       # Windows Explorer
        "lsass.exe",          # Local Security Authority Subsystem Service
        "csrss.exe",          # Client/Server Runtime Subsystem
        "smss.exe",           # Session Manager Subsystem
        "winlogon.exe",       # Windows Logon
        "spoolsv.exe",        # Print Spooler Service
        "taskhostw.exe",      # Task Host
        "dwm.exe",            # Desktop Window Manager
        "cmd.exe",            # Command Prompt
        "powershell.exe",     # PowerShell
        "msedge.exe",         # Microsoft Edge
        "chrome.exe",         # Google Chrome
        "firefox.exe",        # Mozilla Firefox
        "outlook.exe",        # Microsoft Outlook
        "word.exe",           # Microsoft Word
        "excel.exe",          # Microsoft Excel
        "notepad.exe",        # Notepad
        "wmiprvse.exe",       # WMI Provider Host
        "wininit.exe",        # Windows Start-Up Application
        "services.exe",       # Services and Controller app
        "RuntimeBroker.exe",  # Runtime Broker
        "MsMpEng.exe",        # Windows Defender Antivirus
    ]
    
    process_name = random.choice(process_names)
    
    # Generate different paths based on process type
    if process_name in ["svchost.exe", "lsass.exe", "csrss.exe", "smss.exe", "winlogon.exe", "spoolsv.exe", 
                       "wininit.exe", "services.exe", "MsMpEng.exe"]:
        path = f"\\??\\C:\\Windows\\System32\\{process_name}"
        img_path = f"\\Device\\HarddiskVolume2\\Windows\\System32\\{process_name}"
    elif process_name in ["explorer.exe", "taskhostw.exe", "dwm.exe", "RuntimeBroker.exe"]:
        path = f"\\??\\C:\\Windows\\{process_name}"
        img_path = f"\\Device\\HarddiskVolume2\\Windows\\{process_name}"
    elif process_name in ["msedge.exe", "chrome.exe", "firefox.exe"]:
        browsers_path = random.choice([
            "Program Files\\Microsoft\\Edge\\Application",
            "Program Files\\Google\\Chrome\\Application",
            "Program Files\\Mozilla Firefox"
        ])
        path = f"\\??\\C:\\{browsers_path}\\{process_name}"
        img_path = f"\\Device\\HarddiskVolume2\\{browsers_path}\\{process_name}"
    elif process_name in ["outlook.exe", "word.exe", "excel.exe"]:
        office_path = "Program Files\\Microsoft Office\\root\\Office16"
        path = f"\\??\\C:\\{office_path}\\{process_name}"
        img_path = f"\\Device\\HarddiskVolume2\\{office_path}\\{process_name}"
    else:
        path = f"\\??\\C:\\Windows\\System32\\{process_name}"
        img_path = f"\\Device\\HarddiskVolume2\\Windows\\System32\\{process_name}"
    
    # Generate command line arguments if needed
    if process_name == "conhost.exe":
        cmd_line = f"{path} 0xffffffff"
    elif process_name == "cmd.exe":
        cmd_line = f"{path} /c {random.choice(['ipconfig', 'dir', 'whoami', 'net user'])}"
    elif process_name == "powershell.exe":
        cmd_line = f"{path} -Command {random.choice(['Get-Process', 'Get-Service', 'Get-EventLog -LogName System -Newest 5'])}"
    elif process_name == "svchost.exe":
        cmd_line = f"{path} -k {random.choice(['LocalService', 'NetworkService', 'LocalSystemNetworkRestricted'])}"
    else:
        cmd_line = path
    
    return {
        "process_name": process_name,
        "command_line": cmd_line,
        "image_file_name": img_path
    }


def generate_entities(num_hosts: int = 50, num_ips_per_host: int = 2, num_users: int = 100) -> Dict[str, Any]:
    """Generate random entities (hosts, IPs, users) for log generation.
    
    Args:
        num_hosts: Number of hosts to generate.
        num_ips_per_host: Number of IPs to generate per host.
        num_users: Number of users to generate.
        
    Returns:
        A dictionary containing the generated entities.
    """
    domains = ["example.com", "internal.corp", "prod.local", "dev.net", "cloud.internal"]
    entities = {
        "hosts": [],
        "ips": {},  # host_n: [ip1, ip2]
        "users": [generate_username() for _ in range(num_users)]
    }
    for i in range(num_hosts):
        hostname = generate_hostname(domains)
        entities["hosts"].append(hostname)
        entities["ips"][hostname] = [generate_ip_address() for _ in range(num_ips_per_host)]
    return entities


def fill_log_template(template: Dict[str, Any], entities: Dict[str, Any], 
                      customer_id: str, project_id: str, log_type: str,
                      current_time_ms: Optional[int] = None, 
                      current_time_iso: Optional[str] = None) -> Dict[str, Any]:
    """Fill a log template with dynamic data.
    
    Args:
        template: The log template to fill.
        entities: The generated entities to use for filling.
        customer_id: The Chronicle customer ID.
        project_id: The Google Cloud project ID.
        log_type: The type of log.
        current_time_ms: The current time in milliseconds since epoch (optional).
        current_time_iso: The current time in ISO format (optional).
        
    Returns:
        The filled log template as a dictionary.
    """
    log = copy.deepcopy(template)
    
    # Set current time if not provided
    if current_time_ms is None:
        current_dt = datetime.now(timezone.utc)
        current_time_ms = int(current_dt.timestamp() * 1000)
    
    if current_time_iso is None:
        current_dt = datetime.now(timezone.utc)
        current_time_iso = current_dt.isoformat().replace("+05:00", "Z").replace("+00:00", "Z")
    
    # Common fields
    if "EventTime" in log: log["EventTime"] = current_time_ms
    if "EventReceivedTime" in log: log["EventReceivedTime"] = current_time_ms
    if "timestamp" in log: log["timestamp"] = current_time_ms  # For CS_EDR which uses seconds.ms
    if "published" in log: log["published"] = current_time_iso  # For OKTA
    if "time" in log: log["time"] = current_time_iso  # For AZURE_AD
    if "activityDateTime" in log.get("properties", {}): log["properties"]["activityDateTime"] = current_time_iso
    if "createdDateTime" in log.get("properties", {}): log["properties"]["createdDateTime"] = current_time_iso

    chosen_host = random.choice(entities["hosts"])
    if "Hostname" in log: log["Hostname"] = chosen_host
    if "properties" in log and "userDisplayName" in log["properties"]:  # AZURE_AD Signin
        log["properties"]["userDisplayName"] = random.choice(entities["users"])
    if "properties" in log and "userPrincipalName" in log["properties"]:  # AZURE_AD Signin
        log["properties"]["userPrincipalName"] = random.choice(entities["users"]) + "@" + chosen_host.split('.',1)[1]
    if "actor" in log and "alternateId" in log["actor"]:  # OKTA
        log["actor"]["alternateId"] = random.choice(entities["users"]) + "@" + chosen_host.split('.',1)[1]
    if "actor" in log and "displayName" in log["actor"]:  # OKTA
        log["actor"]["displayName"] = random.choice(entities["users"]).capitalize()
    
    # Hostname specific replacements (e.g. in message fields)
    if "Message" in log and isinstance(log["Message"], str):
        log["Message"] = log["Message"].replace("{subject_hostname}", chosen_host.split('.')[0])
        log["Message"] = log["Message"].replace("{domain_name}", chosen_host.split('.',1)[1] if '.' in chosen_host else "CORP")
    
    chosen_ip = random.choice(entities["ips"].get(chosen_host, [generate_ip_address()]))
    if "aip" in log: log["aip"] = chosen_ip  # CS_EDR
    if "IpAddress" in log: log["IpAddress"] = chosen_ip  # WINEVTLOG (some EventIDs)
    if "callerIpAddress" in log: log["callerIpAddress"] = chosen_ip  # AZURE_AD Signin
    if "client" in log and "ipAddress" in log["client"]: log["client"]["ipAddress"] = chosen_ip  # OKTA
    if "request" in log and "ipChain" in log["request"] and log["request"]["ipChain"]:  # OKTA
        log["request"]["ipChain"][0]["ip"] = chosen_ip
    if "properties" in log and "ipAddress" in log["properties"]:  # AZURE_AD Signin
         log["properties"]["ipAddress"] = chosen_ip
    if "protoPayload" in log and "requestMetadata" in log["protoPayload"] and "callerIp" in log["protoPayload"]["requestMetadata"]:  # GCP_CLOUDAUDIT
        log["protoPayload"]["requestMetadata"]["callerIp"] = chosen_ip
    if "Message" in log and isinstance(log["Message"], str):
        log["Message"] = log["Message"].replace("{source_ip}", chosen_ip)

    # User specific
    chosen_user = random.choice(entities["users"])
    if "SubjectUserName" in log: log["SubjectUserName"] = chosen_user.upper()  # WINEVTLOG often uses uppercase
    if "TargetUserName" in log: log["TargetUserName"] = chosen_user  # WINEVTLOG
    if "actor" in log and "displayName" in log["actor"] and log["actor"]["displayName"] is None: log["actor"]["displayName"] = chosen_user.capitalize()  # OKTA
    if "identity" in log: log["identity"] = chosen_user.capitalize()  # AZURE_AD Signin
    if "protoPayload" in log and "authenticationInfo" in log["protoPayload"] and "principalEmail" in log["protoPayload"]["authenticationInfo"]:  # GCP_CLOUDAUDIT
        log["protoPayload"]["authenticationInfo"]["principalEmail"] = chosen_user + "@" + chosen_host.split('.',1)[1]
    if "Message" in log and isinstance(log["Message"], str):
        log["Message"] = log["Message"].replace("{target_username}", chosen_user)

    # Process information (for Windows logs and EDR)
    if log_type in ["WINEVTLOG", "CS_EDR"]:
        process_info = generate_windows_process()
        
        # Update process-related fields
        if "CommandLine" in log: log["CommandLine"] = process_info["command_line"]
        if "ParentBaseFileName" in log: log["ParentBaseFileName"] = process_info["process_name"]
        if "ImageFileName" in log: log["ImageFileName"] = process_info["image_file_name"]
        
        # Update process message if present
        if "Message" in log and isinstance(log["Message"], str) and "Process Name:" in log["Message"]:
            log["Message"] = log["Message"].replace("-", process_info["image_file_name"])

    # IDs and SIDs
    if "RecordNumber" in log: log["RecordNumber"] = random.randint(100000, 90000000)
    if "ActivityID" in log: log["ActivityID"] = f"{{{uuid.uuid4()}}}"
    if "ProcessID" in log: log["ProcessID"] = random.randint(100, 9000)
    if "ThreadID" in log: log["ThreadID"] = random.randint(100, 9000)
    if "TargetSid" in log: log["TargetSid"] = f"S-1-5-21-{random.randint(1000000000,2000000000)}-{random.randint(1000000000,2000000000)}-{random.randint(100000,200000)}"
    if "Message" in log and isinstance(log["Message"], str):
        log["Message"] = log["Message"].replace("{target_sid}", f"S-1-5-21-{random.randint(1000000000,2000000000)}-{random.randint(1000000000,2000000000)}-{random.randint(100000,200000)}")
        log["Message"] = log["Message"].replace("{logon_id}", f"0x{random.randint(0x100000, 0xFFFFFFF):X}")
        log["Message"] = log["Message"].replace("{logon_guid}", f"{{{uuid.uuid4()}}}")

    if "SubjectDomainName" in log: log["SubjectDomainName"] = chosen_host.split('.',1)[1].upper() if '.' in chosen_host else "CORP"
    
    # OKTA specific
    if "authenticationContext" in log and "externalSessionId" in log["authenticationContext"]: log["authenticationContext"]["externalSessionId"] = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    if "uuid" in log: log["uuid"] = str(uuid.uuid4())
    if "transaction" in log and "id" in log["transaction"]: log["transaction"]["id"] = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    if "debugContext" in log and "debugData" in log["debugContext"] and "requestId" in log["debugContext"]["debugData"]:
        log["debugContext"]["debugData"]["requestId"] = ''.join(random.choices(string.ascii_letters + string.digits, k=20)) + "AAABAA"

    # AZURE_AD specific
    if "tenantId" in log: log["tenantId"] = str(uuid.uuid4())
    if "am_tenantId" in log: log["am_tenantId"] = log["tenantId"].upper()  # Often uppercase
    if "correlationId" in log: log["correlationId"] = str(uuid.uuid4())
    if "properties" in log and "id" in log["properties"]: log["properties"]["id"] = str(uuid.uuid4())
    if "properties" in log and "correlationId" in log["properties"]: log["properties"]["correlationId"] = log["correlationId"]
    if "properties"in log and "initiatedBy" in log["properties"] and "user" in log["properties"]["initiatedBy"] and "id" in log["properties"]["initiatedBy"]["user"]:
        log["properties"]["initiatedBy"]["user"]["id"] = f"S-1-5-21-{random.randint(1000000000,2000000000)}-{random.randint(1000000000,2000000000)}-{random.randint(100000,200000)}"
    if "properties" in log and "targetResources" in log["properties"]:
        for res in log["properties"]["targetResources"]:
            if "id" in res: res["id"] = str(uuid.uuid4()) if res.get("type") == "User" else f"{{{uuid.uuid4()}}}"  # Group IDs often in {}
            if "userPrincipalName" in res: res["userPrincipalName"] = random.choice(entities["users"]) + "@" + chosen_host.split('.',1)[1]
            if "modifiedProperties" in res and res["modifiedProperties"] and "newValue" in res["modifiedProperties"][0]:
                res["modifiedProperties"][0]["newValue"] = f"\\\"{{{uuid.uuid4()}}}\\\"" # Group.ObjectID example

    # GCP_CLOUDAUDIT specific
    if "insertId" in log: log["insertId"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    if "logName" in log and "{project_id}" in log["logName"]: log["logName"] = log["logName"].replace("{project_id}", project_id)
    if "operation" in log and "id" in log["operation"]: log["operation"]["id"] = str(random.randint(10**15, 10**19))  # Large number
    if "protoPayload" in log:
        if "authenticationInfo" in log["protoPayload"] and "principalSubject" in log["protoPayload"]["authenticationInfo"]:
            log["protoPayload"]["authenticationInfo"]["principalSubject"] = "user:" + log["protoPayload"]["authenticationInfo"]["principalEmail"]
        if "request" in log["protoPayload"] and "name" in log["protoPayload"]["request"]:
             log["protoPayload"]["request"]["name"] = f"projects/-/serviceAccounts/{chosen_user}@{project_id}.iam.gserviceaccount.com"
        if "resourceName" in log["protoPayload"]:
            log["protoPayload"]["resourceName"] = f"projects/-/serviceAccounts/{random.randint(10**19, 10**20-1)}"
    if "resource" in log and "labels" in log["resource"]:
        if "email_id" in log["resource"]["labels"]: log["resource"]["labels"]["email_id"] = f"{chosen_user}@{project_id}.iam.gserviceaccount.com"
        if "project_id" in log["resource"]["labels"]: log["resource"]["labels"]["project_id"] = project_id
        if "unique_id" in log["resource"]["labels"]: log["resource"]["labels"]["unique_id"] = str(random.randint(10**19, 10**20-1))

    # CS_EDR specific
    if "ParentProcessId" in log: log["ParentProcessId"] = str(random.randint(10**13, 10**14 -1))
    if "SourceProcessId" in log: log["SourceProcessId"] = log["ParentProcessId"]  # Often the same in ProcessRollup
    if "UserSid" in log: log["UserSid"] = f"S-1-5-21-{random.randint(1000000000,2000000000)}-{random.randint(1000000000,2000000000)}-{random.randint(1000,5000)}"
    if "id" in log and log_type == "CS_EDR": log["id"] = str(uuid.uuid4())  # CS_EDR id seems to be a UUID
    if "RawProcessId" in log: log["RawProcessId"] = str(random.randint(1000, 20000))
    if "TargetProcessId" in log: log["TargetProcessId"] = str(random.randint(10**13, 10**14 -1))
    if "SourceThreadId" in log: log["SourceThreadId"] = str(random.randint(10**13, 10**14 -1))
    if "ProcessStartTime" in log: log["ProcessStartTime"] = f"{time.time() - random.uniform(0, 3600):.3f}"  # Randomly in the last hour
    if "aid" in log: log["aid"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    if "cid" in log and customer_id: log["cid"] = customer_id  # Use the provided customer_id for CS_EDR logs

    # Ensure all None placeholders that should have been filled are replaced, or remove them
    final_log = {}
    for k, v in log.items():
        if isinstance(v, str) and v is None:  # Explicitly checking for our None placeholder
            continue  # Skip if it was meant to be replaced but wasn't
        elif v is not None:
            final_log[k] = v
            
    return final_log 