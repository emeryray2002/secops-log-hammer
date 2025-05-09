# SecOps Log Hammer

A Python tool for generating and ingesting synthetic logs into Chronicle.

## Description

SecOps Log Hammer is designed for testing and development purposes. It can generate realistic security logs in various formats (WINEVTLOG, OKTA, AZURE_AD, GCP_CLOUDAUDIT, CS_EDR) and ingest them into Chronicle.

## Features

- Generate realistic security log data
- Support for multiple log formats
- Configurable log volume (by GB or MB)
- Progress tracking
- Automatic forwarder management
- Support for production, staging, and development environments

## Installation

```bash
pip install secops-log-hammer
```

## Requirements

- Python 3.7 or later
- Google Cloud authentication credentials (either Application Default Credentials or a service account key file)
- Chronicle instance access

## Authentication

Log Hammer supports two authentication methods:

### Application Default Credentials (ADC) - Recommended

By default, Log Hammer uses Application Default Credentials. To set up ADC:

```bash
gcloud auth application-default login
```

This will authenticate your account and store credentials locally. No additional parameters are needed when running Log Hammer.

### Service Account Key

Alternatively, you can use a service account key file:

1. Create a service account with appropriate Chronicle permissions
2. Generate a JSON key file for the service account
3. Provide the path to the key file using the `--service-account-path` option

## Usage

```bash
log-hammer --customer_id YOUR_CUSTOMER_ID --project_id YOUR_PROJECT_ID [--region REGION] [--gb 0.1 | --mb 100]
```

The CLI supports both underscore and dash formats for arguments (e.g., `--customer_id` or `--customer-id`).

### Required Arguments

- `--customer_id` / `--customer-id`: Chronicle Customer ID
- `--project_id` / `--project-id`: Google Cloud Project ID

### Log Size Options (specify one)

- `--gigabytes` / `--gb`: Approximate gigabytes of raw logs to generate and ingest
- `--megabytes` / `--mb`: Approximate megabytes of raw logs to generate and ingest
  
If neither option is specified, defaults to 100 MB.

**Note:** You can use the short forms `--gb` and `--mb` instead of `--gigabytes` and `--megabytes` for convenience.

### Other Options

- `--region`: Chronicle API region (e.g., us, europe, asia-southeast1). Special values:
  - `staging`: Use the Chronicle staging environment
  - `dev`: Use the Chronicle development/autopush environment
  - Default: "us"
- `--service_account_path` / `--service-account-path`: Path to GCP service account JSON key file for authentication. If not provided, Application Default Credentials (ADC) will be used.
- `--forwarder_display_name` / `--forwarder-display-name`: Display name for the Chronicle forwarder to be created/used (default: "PythonLogIngestScriptForwarder").
- `--namespace`: Optional asset namespace for the logs. May be required for some log types.
- `--log_types` / `--log-types`: Comma-separated list of log types to generate. If empty, all available types will be used.
- `--labels`: Optional labels to attach to logs in key=value,key2=value2 format or as JSON object.

## Examples

Generate and ingest 0.5 GB of logs into Chronicle in the US region:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --gb 0.5
```

Generate and ingest 100 MB of logs:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --mb 100
```

Use a service account key for authentication:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --mb 50 --service-account-path /path/to/service-account-key.json
```

Generate only specific log types:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --log-types WINEVTLOG,OKTA
```

Generate logs for a staging environment:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --region staging --mb 10
```

Generate logs for a development/autopush environment:

```bash
log-hammer --customer-id my-customer-id --project-id my-gcp-project --region dev --mb 10
```

## License

Apache 2.0 