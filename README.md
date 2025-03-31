# Port and Checkmarx Integration

This script integrates Port with Checkmarx by:
1. Creating a Port access token
2. Checking for and creating a "checkMarxProject" blueprint if it doesn't exist
3. Fetching all projects from Checkmarx
4. Creating Port entities for each Checkmarx project

## Prerequisites

- Python 3.7 or higher
- Port API credentials (Client ID and Client Secret)
- Checkmarx API key

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the following environment variables:
```bash
export PORT_CLIENT_ID="your_port_client_id"
export PORT_CLIENT_SECRET="your_port_client_secret"
export CHECKMARX_BASE_URL="your_checkmarx_base_url"
export CHECKMARX_API_KEY="your_checkmarx_api_key"
```

## Usage

Run the script:
```bash
python port_checkmarx_integration.py
```

The script will:
1. Authenticate with both Port and Checkmarx
2. Check if the "checkMarxProject" blueprint exists in Port
3. Create the blueprint if it doesn't exist
4. Fetch all projects from Checkmarx
5. Create Port entities for each Checkmarx project, linking them to the appropriate service entities

## Notes

- The script assumes that the service name can be extracted from the Checkmarx project name (format: service-name/project-name)
- If a project name doesn't contain a service name, the entire project name will be used as the service identifier
- The script includes error handling and will continue processing even if individual entity creation fails
- The script uses OAuth2 client credentials flow with the Checkmarx API key for authentication 