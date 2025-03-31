import os
import requests
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class PortClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.getport.io/v1"
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        response = requests.post(
            f"{self.base_url}/auth/access_token",
            json={
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["accessToken"]
        self.token_expiry = datetime.now() + timedelta(seconds=data["expiresIn"])
        return self.access_token

    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }

    def get_blueprint(self, identifier: str) -> Optional[Dict]:
        """Get a blueprint by identifier if it exists."""
        try:
            response = requests.get(
                f"{self.base_url}/blueprints/{identifier}",
                headers=self.get_headers()
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def create_blueprint(self, identifier: str, title: str, description: str, properties: Dict = None, relations: Dict = None) -> Dict:
        """Create a new blueprint with the specified configuration."""
        blueprint_data = {
            "identifier": identifier,
            "title": title,
            "description": description,
            "schema": {
                "properties": properties or {},
                "required": []
            },
            "relations": relations or {}
        }
        
        # Debug: Print the blueprint data
        print(f"Creating blueprint with data: {json.dumps(blueprint_data, indent=2)}")
        
        response = requests.post(
            f"{self.base_url}/blueprints",
            headers=self.get_headers(),
            json=blueprint_data
        )
        
        # Debug: Print response content if there's an error
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            
        response.raise_for_status()
        return response.json()

    def create_entity(self, blueprint_id: str, identifier: str, title: str, properties: Dict, relations: Dict) -> Dict:
        """Create a new entity in the specified blueprint."""
        entity_data = {
            "identifier": identifier,
            "title": title,
            "properties": properties,
            "relations": relations
        }
        
        # Debug: Print the entity data
        print(f"Creating entity with data: {json.dumps(entity_data, indent=2)}")
        
        response = requests.post(
            f"{self.base_url}/blueprints/{blueprint_id}/entities",
            headers=self.get_headers(),
            json=entity_data
        )
        response.raise_for_status()
        return response.json()

class CheckmarxClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.access_token = None
        self.auth_url = "https://deu.iam.checkmarx.net/auth/realms/port-nfr/protocol/openid-connect/token"

    def get_access_token(self) -> str:
        """Get access token from Checkmarx using API key."""
        if self.access_token:
            return self.access_token

        response = requests.post(
            self.auth_url,
            data={
                "grant_type": "refresh_token",
                "client_id": "ast-app",
                "refresh_token": self.api_key
            }
        )
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return self.access_token

    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }

    def get_projects(self) -> List[Dict]:
        """Get all projects from Checkmarx."""
        response = requests.get(
            f"{self.base_url}/api/projects",
            headers=self.get_headers()
        )
        response.raise_for_status()
        data = response.json()
        return data.get("projects", [])

def main():
    # Initialize clients
    port_client = PortClient(
        client_id=os.getenv("PORT_CLIENT_ID"),
        client_secret=os.getenv("PORT_CLIENT_SECRET")
    )

    checkmarx_client = CheckmarxClient(
        base_url=os.getenv("CHECKMARX_BASE_URL"),
        api_key=os.getenv("CHECKMARX_API_KEY")
    )

    # Create blueprint if it doesn't exist
    blueprint = port_client.get_blueprint("checkMarxProject")
    if not blueprint:
        print("Creating checkMarxProject blueprint...")
        port_client.create_blueprint(
            identifier="checkMarxProject",
            title="Checkmarx Project",
            description="Represents a Checkmarx project",
            properties={
                "description": {
                    "type": "string",
                    "title": "Description",
                    "description": "Project description"
                },
                "projectId": {
                    "type": "string",
                    "title": "Project ID",
                    "description": "Unique identifier for the project"
                },
                "lastScanDate": {
                    "type": "string",
                    "title": "Last Scan Date",
                    "description": "Date of the last scan"
                }
            },
            relations={}
        )
        print("checkMarxProject blueprint created successfully")
    else:
        print("checkMarxProject blueprint already exists")

    # Get all projects from Checkmarx
    print("Fetching projects from Checkmarx...")
    projects = checkmarx_client.get_projects()
    
    if not projects:
        print("No projects found in Checkmarx")
        return

    # Create entities in Port for each project
    for project in projects:
        try:
            project_name = project.get("name", "")
            project_id = str(project.get("id", project_name))
            
            # Create the Checkmarx project entity
            port_client.create_entity(
                blueprint_id="checkMarxProject",
                identifier=project_id,
                title=project_name,
                properties={
                    "description": project.get("description", ""),
                    "projectId": project_id,
                    "lastScanDate": project.get("lastScanDate", "")
                },
                relations={}
            )
            print(f"Created entity for project: {project_name}")
        except Exception as e:
            print(f"Error creating entity for project {project_name if 'project_name' in locals() else 'unknown'}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    main() 