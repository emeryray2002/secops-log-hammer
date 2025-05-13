"""Log generators module for the SecOps Log Hammer package."""

import copy
import json
import random
import string
import time
import uuid
import ipaddress
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union


def generate_ip_address() -> str:
    """Generate a random IP address.
    
    Returns:
        A random IPv4 address as a string.
    """
    return f"{random.randint(1, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"


def generate_ipv6_address() -> str:
    """Generate a random IPv6 address.
    
    Returns:
        A random IPv6 address as a string.
    """
    segments = [f"{random.randint(0, 65535):x}" for _ in range(8)]
    return ":".join(segments)


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


def generate_mobile_device_info() -> Dict[str, str]:
    """Generate random mobile device information.
    
    Returns:
        A dictionary containing mobile device information.
    """
    device_types = ["iPhone", "iPad", "Android Phone", "Android Tablet"]
    os_versions = {
        "iPhone": ["iOS 15.4.1", "iOS 16.1.2", "iOS 16.5", "iOS 17.0", "iOS 17.1", "iOS 18.2.0"],
        "iPad": ["iPadOS 15.6", "iPadOS 16.2", "iPadOS 16.5", "iPadOS 17.1"],
        "Android Phone": ["Android 11", "Android 12", "Android 13", "Android 14"],
        "Android Tablet": ["Android 11", "Android 12", "Android 13", "Android 14"]
    }
    
    device_type = random.choice(device_types)
    os_version = random.choice(os_versions[device_type])
    
    # Generate device model based on type
    if "iPhone" in device_type:
        model = f"iPhone {random.choice(['11', '12', '13', '14', '15', 'SE', 'Pro Max'])}"
    elif "iPad" in device_type:
        model = f"iPad {random.choice(['Air', 'Pro', 'Mini', '10.2-inch', '10.9-inch'])}"
    elif "Android" in device_type:
        manufacturers = ["Samsung", "Google", "OnePlus", "Xiaomi", "Motorola"]
        models = {
            "Samsung": ["Galaxy S22", "Galaxy S23", "Galaxy Note 20", "Galaxy A53"],
            "Google": ["Pixel 6", "Pixel 7", "Pixel 7a", "Pixel 8"],
            "OnePlus": ["9 Pro", "10T", "11", "Nord"],
            "Xiaomi": ["Redmi Note 11", "Mi 12", "Poco F4"],
            "Motorola": ["Edge 30", "G Power", "Razr"]
        }
        manufacturer = random.choice(manufacturers)
        model = f"{manufacturer} {random.choice(models[manufacturer])}"
    
    device_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
    
    return {
        "device_type": device_type,
        "model": model,
        "os_version": os_version,
        "device_id": device_id,
        "is_managed": random.choice(["true", "false"]),
        "is_compliant": random.choice(["true", "false"]),
        "display_name": f"R{random.randint(1000000, 9999999)}"
    }


def generate_cloud_resource_info(project_id: str) -> Dict[str, str]:
    """Generate random cloud resource information.
    
    Args:
        project_id: The Google Cloud project ID.
        
    Returns:
        A dictionary containing cloud resource information.
    """
    resource_types = ["compute_instance", "storage_bucket", "cloud_function", "gke_cluster", "bigquery_dataset"]
    regions = ["us-central1", "us-east1", "us-west1", "europe-west1", "asia-east1", "australia-southeast1"]
    
    resource_type = random.choice(resource_types)
    region = random.choice(regions)
    
    # Generate resource name based on type
    if resource_type == "compute_instance":
        name = f"vm-{random.choice(['prod', 'dev', 'test', 'staging'])}-{random.randint(1000, 9999)}"
    elif resource_type == "storage_bucket":
        name = f"{project_id}-{random.choice(['data', 'backup', 'assets', 'logs'])}-{random.randint(100, 999)}"
    elif resource_type == "cloud_function":
        name = f"func-{random.choice(['process', 'transform', 'analyze', 'trigger'])}-{random.randint(100, 999)}"
    elif resource_type == "gke_cluster":
        name = f"cluster-{random.choice(['prod', 'dev', 'test'])}-{random.randint(1, 5)}"
    elif resource_type == "bigquery_dataset":
        name = f"{random.choice(['raw', 'processed', 'analytics', 'reporting'])}_data"
    else:
        name = f"resource-{random.randint(1000, 9999)}"
    
    return {
        "resource_type": resource_type,
        "name": name,
        "region": region,
        "project_id": project_id,
        "resource_id": str(random.randint(10**19, 10**20 - 1))
    }


def generate_service_account_info(project_id: str) -> Dict[str, str]:
    """Generate random service account information.
    
    Args:
        project_id: The Google Cloud project ID.
        
    Returns:
        A dictionary containing service account information.
    """
    purposes = ["compute", "storage", "bigquery", "logging", "deployment", "monitoring"]
    purpose = random.choice(purposes)
    
    sa_name = f"{purpose}-sa-{random.randint(100, 999)}"
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    sa_id = str(random.randint(10**19, 10**20 - 1))
    
    return {
        "name": sa_name,
        "email": sa_email,
        "id": sa_id,
        "project_id": project_id,
        "display_name": f"Service Account for {purpose.capitalize()}"
    }


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


def generate_dns_info() -> Dict[str, Any]:
    """Generate random DNS request information.
    
    Returns:
        A dictionary containing DNS request information.
    """
    # Common TLDs and subdomains
    tlds = [".com", ".org", ".net", ".io", ".cloud", ".ai", ".dev", ".app"]
    common_domains = ["example", "acme", "test", "dev", "prod", "internal", "corp", "cloud"]
    subdomains = ["api", "app", "auth", "login", "admin", "portal", "cdn", "static", "media", "download"]
    
    # Sometimes generate suspicious-looking domains
    suspicious_patterns = [
        lambda: f"{''.join(random.choices(string.ascii_lowercase, k=random.randint(10, 20)))}{random.choice(tlds)}",
        lambda: f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 15)))}.{''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))}.{random.choice(['com', 'net', 'ru', 'cn'])}",
        lambda: f"{random.choice(common_domains)}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10)))}.{''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 8)))}.{random.choice(['me', 'cc', 'biz', 'info'])}"
    ]
    
    # Decide whether to generate a normal or suspicious domain
    if random.random() < 0.8:  # 80% normal domains
        if random.random() < 0.6:  # With subdomain
            domain = f"{random.choice(subdomains)}.{random.choice(common_domains)}{random.choice(tlds)}"
        else:  # Just domain
            domain = f"{random.choice(common_domains)}{random.choice(tlds)}"
    else:  # 20% suspicious domains
        domain = random.choice(suspicious_patterns)()
    
    record_types = ["A", "AAAA", "MX", "TXT", "CNAME", "NS", "SRV"]
    
    return {
        "domain": domain,
        "record_type": random.choice(record_types),
        "request_count": random.randint(1, 5),
        "is_suspicious": random.random() < 0.2,  # 20% chance of being marked suspicious
        "protocol": random.choice(["UDP", "TCP"]),
        "interface_index": random.randint(0, 10)
    }


def generate_network_connection() -> Dict[str, Any]:
    """Generate random network connection information.
    
    Returns:
        A dictionary containing network connection information.
    """
    protocols = {
        "6": "TCP",
        "17": "UDP",
        "1": "ICMP",
        "58": "ICMPv6"
    }
    
    protocol_num = random.choice(list(protocols.keys()))
    protocol_name = protocols[protocol_num]
    
    # Common ports and their descriptions
    common_ports = {
        "20": "FTP Data",
        "21": "FTP Control",
        "22": "SSH",
        "23": "Telnet",
        "25": "SMTP",
        "53": "DNS",
        "80": "HTTP",
        "110": "POP3",
        "123": "NTP",
        "143": "IMAP",
        "443": "HTTPS",
        "445": "SMB",
        "993": "IMAPS",
        "995": "POP3S",
        "3306": "MySQL",
        "3389": "RDP",
        "5432": "PostgreSQL",
        "8080": "HTTP Alternate",
        "8443": "HTTPS Alternate"
    }
    
    # Sometimes use common ports, sometimes random high ports
    if random.random() < 0.7:  # 70% common ports
        remote_port = random.choice(list(common_ports.keys()))
        remote_port_desc = common_ports[remote_port]
    else:  # 30% random high ports
        remote_port = str(random.randint(10000, 65535))
        remote_port_desc = "Unknown"
    
    # Local port is usually a high random port
    local_port = str(random.randint(10000, 65535))
    
    # Decide connection direction
    connection_direction = random.choice(["0", "1"])  # 0 = outbound, 1 = inbound
    
    # IP versions can be mixed
    ip_version = random.choice(["4", "6"])
    
    return {
        "protocol_number": protocol_num,
        "protocol_name": protocol_name,
        "local_port": local_port,
        "remote_port": remote_port,
        "remote_port_description": remote_port_desc,
        "connection_direction": connection_direction,
        "connection_flags": str(random.randint(0, 15)),
        "ip_version": ip_version
    }


def generate_authentication_info() -> Dict[str, Any]:
    """Generate random authentication information.
    
    Returns:
        A dictionary containing authentication information.
    """
    auth_methods = ["Password", "OAuth", "SAML", "Kerberos", "Certificate", "Windows Integrated", 
                   "MultiFactor", "Phone", "FIDO", "App", "SMS", "Email"]
    
    auth_results = [
        {"result": "SUCCESS", "reason": None},
        {"result": "FAILURE", "reason": "Invalid username or password"},
        {"result": "FAILURE", "reason": "Account locked"},
        {"result": "FAILURE", "reason": "Account disabled"},
        {"result": "FAILURE", "reason": "MFA required"},
        {"result": "CHALLENGE", "reason": "Additional verification required"},
        {"result": "FAILURE", "reason": "IP address not allowed"},
        {"result": "FAILURE", "reason": "Expired credentials"}
    ]
    
    # Weight success higher than failures
    result = random.choices(
        auth_results,
        weights=[0.7] + [0.3/7] * 7,  # 70% success, 30% distributed among failures
        k=1
    )[0]
    
    # For MFA, generate additional details
    if "MultiFactor" in auth_methods:
        mfa_types = ["SMS", "Phone call", "Authenticator app", "Security key", "Email"]
        mfa_type = random.choice(mfa_types)
    else:
        mfa_type = None
    
    # Generate auth context details
    auth_context = {
        "auth_method": random.choice(auth_methods),
        "result": result["result"],
        "reason": result["reason"],
        "mfa_type": mfa_type,
        "mfa_completed": True if result["result"] == "SUCCESS" and mfa_type else False,
        "auth_protocol": random.choice(["OAuth 2.0", "SAML 2.0", "OpenID Connect", "WS-Federation", "WS-Trust", "Basic", "NTLM", "Kerberos"]),
        "auth_step": random.randint(0, 3),
        "session_id": ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    }
    
    return auth_context


def generate_security_alert() -> Dict[str, Any]:
    """Generate random security alert information.
    
    Returns:
        A dictionary containing security alert information.
    """
    alert_types = [
        "Suspicious login attempt",
        "Brute force attack",
        "Account compromise",
        "Data exfiltration",
        "Malware detection",
        "Command and control communication",
        "Privilege escalation",
        "Unusual admin activity",
        "Password spray attack",
        "Suspicious process execution",
        "Lateral movement",
        "Suspicious network activity"
    ]
    
    severities = ["Low", "Medium", "High", "Critical"]
    # Weight distribution for severity
    severity_weights = [0.4, 0.3, 0.2, 0.1]  # More low/medium than high/critical
    
    # Status options
    statuses = ["New", "In Progress", "Resolved", "Dismissed", "False Positive"]
    status_weights = [0.4, 0.3, 0.2, 0.05, 0.05]  # More new/in progress than resolved
    
    # MITRE ATT&CK techniques
    mitre_techniques = [
        {"id": "T1078", "name": "Valid Accounts", "tactic": "Initial Access"},
        {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access"},
        {"id": "T1566", "name": "Phishing", "tactic": "Initial Access"},
        {"id": "T1053", "name": "Scheduled Task/Job", "tactic": "Execution"},
        {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution"},
        {"id": "T1098", "name": "Account Manipulation", "tactic": "Persistence"},
        {"id": "T1134", "name": "Access Token Manipulation", "tactic": "Privilege Escalation"},
        {"id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation"},
        {"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery"},
        {"id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control"}
    ]
    
    # Select 1-3 techniques
    selected_techniques = random.sample(mitre_techniques, k=random.randint(1, 3))
    
    return {
        "alert_type": random.choice(alert_types),
        "severity": random.choices(severities, weights=severity_weights, k=1)[0],
        "status": random.choices(statuses, weights=status_weights, k=1)[0],
        "detection_time": int(time.time() - random.randint(0, 86400)),  # Within the last 24 hours
        "alert_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        "source": random.choice(["EDR", "SIEM", "Firewall", "IDS", "DLP", "Cloud Security", "Antivirus"]),
        "mitre_techniques": selected_techniques,
        "confidence": random.randint(50, 100)
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
    if "am_tenantId" in log: log["am_tenantId"] = log["tenantId"].upper() if "tenantId" in log else str(uuid.uuid4()).upper()
    if "correlationId" in log: log["correlationId"] = str(uuid.uuid4())
    if "properties" in log and "id" in log["properties"]: log["properties"]["id"] = str(uuid.uuid4())
    if "properties" in log and "correlationId" in log["properties"]: log["properties"]["correlationId"] = log["correlationId"] if "correlationId" in log else str(uuid.uuid4())
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
        
        # Add MITRE ATT&CK info to GCP logs (sometimes)
        if random.random() < 0.3 and "requestMetadata" in log["protoPayload"]:
            sec_info = generate_security_alert()
            if "metadata" not in log["protoPayload"]:
                log["protoPayload"]["metadata"] = {}
            log["protoPayload"]["metadata"]["securityInfo"] = {
                "threatDetails": {
                    "severity": sec_info["severity"],
                    "techniques": [t["id"] for t in sec_info["mitre_techniques"]],
                    "confidence": sec_info["confidence"]
                }
            }
            
    if "resource" in log and "labels" in log["resource"]:
        if "email_id" in log["resource"]["labels"]: log["resource"]["labels"]["email_id"] = f"{chosen_user}@{project_id}.iam.gserviceaccount.com"
        if "project_id" in log["resource"]["labels"]: log["resource"]["labels"]["project_id"] = project_id
        if "unique_id" in log["resource"]["labels"]: log["resource"]["labels"]["unique_id"] = str(random.randint(10**19, 10**20-1))
        if "location" in log["resource"]["labels"] and not log["resource"]["labels"]["location"]:
            cloud_info = generate_cloud_resource_info(project_id)
            log["resource"]["labels"]["location"] = cloud_info["region"]

    # CS_EDR specific
    if "ParentProcessId" in log: log["ParentProcessId"] = str(random.randint(10**13, 10**14 -1))
    if "SourceProcessId" in log: log["SourceProcessId"] = log["ParentProcessId"] if "ParentProcessId" in log else str(random.randint(10**13, 10**14 -1))
    if "UserSid" in log: log["UserSid"] = f"S-1-5-21-{random.randint(1000000000,2000000000)}-{random.randint(1000000000,2000000000)}-{random.randint(1000,5000)}"
    if "id" in log and log_type == "CS_EDR": log["id"] = str(uuid.uuid4())  # CS_EDR id seems to be a UUID
    if "RawProcessId" in log: log["RawProcessId"] = str(random.randint(1000, 20000))
    if "TargetProcessId" in log: log["TargetProcessId"] = str(random.randint(10**13, 10**14 -1))
    if "SourceThreadId" in log: log["SourceThreadId"] = str(random.randint(10**13, 10**14 -1))
    if "ProcessStartTime" in log: log["ProcessStartTime"] = f"{time.time() - random.uniform(0, 3600):.3f}"  # Randomly in the last hour
    if "aid" in log: log["aid"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    if "cid" in log and customer_id: log["cid"] = customer_id  # Use the provided customer_id for CS_EDR logs
    
    # Mobile device related information
    if "event_platform" in log and log["event_platform"] in ["iOS", "Mac", "Lin"]:
        if log["event_platform"] == "iOS":
            mobile_info = generate_mobile_device_info()
            # Fill in iOS specific details
            if "deviceDetail" in log:
                if not isinstance(log["deviceDetail"], dict):
                    log["deviceDetail"] = {}
                log["deviceDetail"]["deviceId"] = mobile_info["device_id"]
                log["deviceDetail"]["displayName"] = mobile_info["display_name"]
                log["deviceDetail"]["isCompliant"] = mobile_info["is_compliant"] == "true"
                log["deviceDetail"]["isManaged"] = mobile_info["is_managed"] == "true"
                log["deviceDetail"]["operatingSystem"] = mobile_info["os_version"]
                
            # Set battery info for iOS logs with MobilePowerStats
            if "event_simpleName" in log and log["event_simpleName"] == "MobilePowerStats":
                log["BatteryLevel"] = str(random.randint(1, 100))
                log["BatteryStatus"] = str(random.choice([0, 1, 2, 3]))  # 0=unknown, 1=unplugged, 2=charging, 3=full
            
            # Set ApplicationName for ProcessWitness events
            if "event_simpleName" in log and log["event_simpleName"] == "ProcessWitness":
                ios_apps = [".com.apple.purplebuddy", "com.apple.mobilesafari", "com.apple.mobilemail", 
                           "com.apple.mobileslideshow", "com.apple.mobilenotes", "com.apple.Maps"]
                log["ApplicationName"] = random.choice(ios_apps)
                log["ApplicationVersion"] = f"{random.randint(1,15)}.{random.randint(0,9)}.{random.randint(0,9)}"
                log["ApplicationUniqueIdentifier"] = ''.join(random.choices(string.hexdigits.lower(), k=40))
        
        # Set Linux specific details
        elif log["event_platform"] == "Lin":
            if "event_simpleName" in log and log["event_simpleName"] == "CriticalFileAccessed":
                critical_files = ["/etc/shadow", "/etc/passwd", "/etc/sudoers", "/etc/ssh/sshd_config", 
                                 "/root/.ssh/authorized_keys", "/etc/crontab", "/etc/hosts"]
                log["TargetFileName"] = random.choice(critical_files)
                log["GID"] = str(random.choice([0, 1000]))  # 0 = root, 1000 = common user
                log["UID"] = str(random.choice([0, 1000]))
                log["UnixMode"] = str(random.choice([32768, 33152, 33024]))  # Different permission modes

    # Network connection related fields
    if "event_simpleName" in log and ("NetworkConnect" in log["event_simpleName"] or "NetworkReceive" in log["event_simpleName"]):
        network_info = generate_network_connection()
        
        if "LocalPort" in log: log["LocalPort"] = network_info["local_port"]
        if "RemotePort" in log: log["RemotePort"] = network_info["remote_port"]
        if "Protocol" in log: log["Protocol"] = network_info["protocol_number"]
        if "ConnectionDirection" in log: log["ConnectionDirection"] = network_info["connection_direction"]
        if "ConnectionFlags" in log: log["ConnectionFlags"] = network_info["connection_flags"]
    
    # DNS request related fields
    if "event_simpleName" in log and ("DnsRequest" in log["event_simpleName"] or "SuspiciousDnsRequest" in log["event_simpleName"]):
        dns_info = generate_dns_info()
        
        if "DomainName" in log: log["DomainName"] = dns_info["domain"]
        if "DnsRequestCount" in log: log["DnsRequestCount"] = str(dns_info["request_count"])
        if "RequestType" in log: log["RequestType"] = "1"  # 1 = A record
        if "Protocol" in log and not log["Protocol"]: log["Protocol"] = dns_info["protocol"]
        
        # For suspicious DNS requests, add extra details
        if "event_simpleName" in log and log["event_simpleName"] == "SuspiciousDnsRequest":
            if "jsonPayload" not in log:
                log["jsonPayload"] = {}
            log["jsonPayload"]["suspiciousIndicators"] = {
                "reason": random.choice([
                    "Domain generation algorithm detected",
                    "Newly registered domain",
                    "Known malware command and control",
                    "High entropy domain name",
                    "Uncommon TLD usage"
                ]),
                "score": random.randint(70, 100)
            }

    # Ensure all None placeholders that should have been filled are replaced, or remove them
    final_log = {}
    for k, v in log.items():
        if isinstance(v, str) and v is None:  # Explicitly checking for our None placeholder
            continue  # Skip if it was meant to be replaced but wasn't
        elif v is not None:
            final_log[k] = v
            
    return final_log 