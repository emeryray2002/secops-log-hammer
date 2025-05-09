#!/usr/bin/env python3
"""Command-line interface for the SecOps Log Hammer package."""

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Optional tqdm import for progress bar
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from secops_log_hammer import __version__
from secops_log_hammer.auth import SecOpsAuth
from secops_log_hammer.client import ChronicleClient
from secops_log_hammer.exceptions import APIError
from secops_log_hammer.generators import generate_entities, fill_log_template
from secops_log_hammer.log_ingest import get_or_create_forwarder, ingest_logs
from secops_log_hammer.templates import LOG_TEMPLATES


def main() -> None:
    """Run the SecOps Log Hammer CLI tool.
    
    This function parses command-line arguments, initializes the Chronicle client,
    and runs the log generation and ingestion process.
    """
    parser = argparse.ArgumentParser(description="Generate and ingest synthetic logs into Chronicle.")
    # Support both dash and underscore formats for all arguments
    parser.add_argument("--customer_id", "--customer-id", dest="customer_id", required=True, help="Chronicle Customer ID.")
    parser.add_argument("--project_id", "--project-id", dest="project_id", required=True, help="Google Cloud Project ID.")
    parser.add_argument("--region", required=False, default="us", help="Chronicle API region (e.g., us, europe, asia-southeast1). Use 'staging' for the staging environment.")
    
    # Add size options with default of None to check which ones are specified
    size_group = parser.add_argument_group("Log Size Options (specify one)")
    size_group.add_argument("--gigabytes", "--gb", dest="gigabytes", type=float, help="Approximate gigabytes of raw logs to generate and ingest.")
    size_group.add_argument("--megabytes", "--mb", dest="megabytes", type=float, help="Approximate megabytes of raw logs to generate and ingest.")
    
    parser.add_argument("--service_account_path", "--service-account-path", dest="service_account_path", help="Optional path to GCP service account JSON key file for authentication. If not provided, Application Default Credentials (ADC) will be used.")
    parser.add_argument("--forwarder_display_name", "--forwarder-display-name", dest="forwarder_display_name", default="PythonLogIngestScriptForwarder", help="Display name for the Chronicle forwarder to be created/used.")
    parser.add_argument("--namespace", help="Optional asset namespace for the logs.")
    parser.add_argument("--log_types", "--log-types", dest="log_types", default="", help="Comma-separated list of log types to generate. If empty, all available types will be used.")
    parser.add_argument("--labels", help="Optional labels to attach to logs in key=value,key2=value2 format or as JSON object.")
    parser.add_argument("--version", action="version", version=f"secops-log-hammer {__version__}")

    args = parser.parse_args()

    # Determine target size in bytes based on provided arguments
    target_size_gb = 0
    if args.gigabytes is not None:
        # If gigabytes is specified, use it
        target_size_gb = args.gigabytes
        size_description = f"{target_size_gb} GB"
    elif args.megabytes is not None:
        # If only megabytes is specified, convert to GB
        target_size_gb = args.megabytes / 1024
        size_description = f"{args.megabytes} MB"
    else:
        # Default to 100 MB
        target_size_gb = 100 / 1024  # 100 MB in GB
        size_description = "100 MB (default)"

    print(f"Starting log ingestion script...")
    print(f"  Customer ID: {args.customer_id}")
    print(f"  Project ID: {args.project_id}")
    print(f"  Region: {args.region}")
    print(f"  Target Size: {size_description}")
    if args.service_account_path:
        print(f"  Service Account: {args.service_account_path}")
    else:
        print("  Authentication: Using Application Default Credentials (ADC)")
    print(f"  Forwarder Name: {args.forwarder_display_name}")
    if args.namespace:
        print(f"  Namespace: {args.namespace}")
    
    # Parse labels if provided
    labels = None
    if args.labels:
        print(f"  Labels: {args.labels}")
        # Try parsing as JSON first
        try:
            labels = json.loads(args.labels)
        except json.JSONDecodeError:
            # If not valid JSON, try parsing as comma-separated key=value pairs
            labels = {}
            for pair in args.labels.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    labels[key.strip()] = value.strip()
                else:
                    print(f"Warning: Ignoring invalid label format: {pair}", file=sys.stderr)
            
            if not labels:
                print("Warning: No valid labels found. Labels should be in JSON format or comma-separated key=value pairs.", file=sys.stderr)
    
    # Authentication and Client Setup
    try:
        auth = SecOpsAuth(service_account_path=args.service_account_path)
        chronicle_client = ChronicleClient(
            customer_id=args.customer_id,
            project_id=args.project_id,
            region=args.region,
            auth=auth
        )
        print("Successfully authenticated and Chronicle client initialized.")
    except Exception as e:
        print(f"Error during authentication or client setup: {e}", file=sys.stderr)
        print("Please ensure your GCP authentication is configured correctly (ADC or service account).", file=sys.stderr)
        sys.exit(1)

    # Determine if we need a namespace for the forwarder
    namespace = args.namespace
    if not namespace and any(lt.startswith("GCP_") for lt in LOG_TEMPLATES.keys()):
        namespace = "gcp"
        print(f"  Auto-detected need for GCP logs: Using default namespace '{namespace}'")

    # Get or Create Forwarder
    print(f"\nGetting or creating forwarder '{args.forwarder_display_name}'...")
    forwarder_id = get_or_create_forwarder(
        client=chronicle_client, 
        display_name=args.forwarder_display_name,
        namespace=namespace
    )
    print(f"Using Forwarder ID: {forwarder_id}")

    # Get available log types
    available_log_types = list(LOG_TEMPLATES.keys())
    print(f"Available log types: {', '.join(available_log_types)}")
    
    # Filter log types if specified
    if args.log_types:
        selected_log_types = [lt.strip() for lt in args.log_types.split(",")]
        # Check if all specified log types are valid
        invalid_types = [lt for lt in selected_log_types if lt not in available_log_types]
        if invalid_types:
            print(f"Warning: Ignoring invalid log types: {', '.join(invalid_types)}", file=sys.stderr)
        
        selected_log_types = [lt for lt in selected_log_types if lt in available_log_types]
        if not selected_log_types:
            print("Error: No valid log types specified. Please use one or more of: " + 
                  ", ".join(available_log_types), file=sys.stderr)
            sys.exit(1)
    else:
        selected_log_types = available_log_types
    
    print(f"Selected log types for generation: {', '.join(selected_log_types)}")

    # Generate Entities
    print("\nGenerating synthetic entities...")
    entities = generate_entities()
    print(f"Generated {len(entities['hosts'])} hostnames, IPs for each, and {len(entities['users'])} usernames.")

    target_bytes = target_size_gb * (1024**3)
    ingested_bytes = 0
    total_logs_sent = 0
    
    # Initialize tqdm progress bar if available
    pbar = None
    if tqdm:
        pbar = tqdm(total=int(target_bytes), unit='B', unit_scale=True, desc="Ingesting Logs")

    log_type_ingestion_stats = {log_type: {"count": 0, "bytes": 0} for log_type in LOG_TEMPLATES.keys()}
    failed_log_types = set()

    # We'll send logs in batches for efficiency
    BATCH_SIZE = 50  # Number of logs per API call

    print("\nStarting log generation and ingestion loop...")
    try:
        while ingested_bytes < target_bytes:
            logs_batch = []
            batch_bytes_to_send = 0
            
            # Select a log type randomly from the selected types excluding failed ones
            available_types = [lt for lt in selected_log_types if lt not in failed_log_types]
            if not available_types:
                print("All selected log types have failed ingestion. Stopping.")
                break
                
            log_type_to_generate = random.choice(available_types)
            templates_for_type = LOG_TEMPLATES[log_type_to_generate]
            
            if not templates_for_type:
                print(f"Warning: No templates defined for log type {log_type_to_generate}, skipping.", file=sys.stderr)
                continue

            # Determine if we need special labels for this log type
            log_type_labels = labels
            if log_type_to_generate.startswith("GCP_") and not log_type_labels:
                log_type_labels = {"source": "log-hammer", "project": args.project_id}

            for _ in range(BATCH_SIZE):
                if ingested_bytes >= target_bytes:
                    break  # Stop if target is reached within a batch generation

                current_dt = datetime.now(timezone.utc)
                current_time_iso = current_dt.isoformat().replace("+05:00","Z").replace("+00:00", "Z")  # Ensure 'Z' for UTC
                current_time_ms = int(current_dt.timestamp() * 1000)

                template = random.choice(templates_for_type)
                
                # Pass customer_id and project_id for templates that might need them
                log_dict = fill_log_template(
                    template, 
                    entities, 
                    args.customer_id, 
                    args.project_id,
                    log_type_to_generate,
                    current_time_ms, 
                    current_time_iso
                )
                
                # The "data" field should be a JSON string for Chronicle ingestion API
                log_entry_for_api = {
                    "data": json.dumps(log_dict), 
                    "log_entry_time": current_time_iso,
                    "collection_time": current_time_iso
                }
                logs_batch.append(log_entry_for_api)
                batch_bytes_to_send += len(log_entry_for_api["data"].encode('utf-8'))  # Approximate size of raw log data

            if not logs_batch:
                break  # Exit if no logs were generated (e.g., target met)

            try:
                # Ingest the logs with the appropriate labels
                num_sent, bytes_in_batch = ingest_logs(
                    client=chronicle_client, 
                    log_type=log_type_to_generate, 
                    logs=logs_batch, 
                    forwarder_id=forwarder_id,
                    namespace=None,  # Namespace is now set on the forwarder, not individual logs
                    labels=log_type_labels
                )
                
                ingested_bytes += bytes_in_batch
                total_logs_sent += num_sent
                log_type_ingestion_stats[log_type_to_generate]["count"] += num_sent
                log_type_ingestion_stats[log_type_to_generate]["bytes"] += bytes_in_batch

                if pbar:
                    pbar.update(bytes_in_batch)
                else:
                    target_mb = target_size_gb * 1024
                    print(f"  {log_type_to_generate}: Sent {num_sent} logs ({bytes_in_batch / (1024*1024):.3f} MB). Total: {ingested_bytes / (1024*1024):.3f} MB / {target_mb:.3f} MB")
            
            except APIError as e:
                failed_log_types.add(log_type_to_generate)
                print(f"Error during batch ingestion for {log_type_to_generate}: {e}", file=sys.stderr)
                print(f"Will not attempt further ingestion of {log_type_to_generate} logs", file=sys.stderr)
                
                # If all log types have failed, exit
                if len(failed_log_types) == len(selected_log_types):
                    print("All selected log types have failed ingestion. Exiting.", file=sys.stderr)
                    break

    except KeyboardInterrupt:
        print("\nInterrupted by user. Finishing up...")
    finally:
        if pbar:
            pbar.close()

    print("\n--- Ingestion Summary ---")
    print(f"Total Logs Sent: {total_logs_sent}")
    print(f"Total Bytes Ingested: {ingested_bytes / (1024**3):.4f} GB ({ingested_bytes / (1024**2):.2f} MB)")
    print("\nBreakdown by Log Type:")
    for log_type, stats in log_type_ingestion_stats.items():
        if stats["count"] > 0:
            print(f"  {log_type}: {stats['count']} logs, {stats['bytes'] / (1024**2):.3f} MB")
    
    if failed_log_types:
        print("\nFailed Log Types:")
        for log_type in failed_log_types:
            print(f"  {log_type}")
        print("\nTroubleshooting tips:")
        print("  1. Check that your service account has the right permissions for these log types")
        print("  2. Verify that your Chronicle instance supports these log types")
        print("  3. Run with specific log types using --log_types to test only those that work")
        print("  4. For GCP logs, ensure the forwarder has the correct asset_namespace")
    
    print("\nLog ingestion process finished.")


if __name__ == "__main__":
    main() 