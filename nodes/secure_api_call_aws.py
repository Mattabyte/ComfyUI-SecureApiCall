import requests
import json
import server
import os
import urllib.parse
from boto3.session import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from typing import Optional

from .util import ComfyAnyType

class SecureApiCallAws:
    ALLOWED_SCHEMES = {'https', 'http'}
    
    @staticmethod
    def validate_url(url: str) -> Optional[str]:
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in SecureApiCallAws.ALLOWED_SCHEMES:
                return f"URL scheme must be one of: {', '.join(SecureApiCallAws.ALLOWED_SCHEMES)}"
            return None
        except Exception:
            return "Invalid URL format"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (ComfyAnyType("*"), {}),
                "full_comfyui_info": ('BOOLEAN', {'default': True}),
                "timeout": ('FLOAT', {'default': 3, 'min': 0, 'max': 60}),
                "verify_ssl": ('BOOLEAN', {'default': True}),
                "api_url": ("STRING", {'default': 'https://localhost:9001/', 'tooltip': 'The API Url (USE $ENV.API_URL) and set COMFYUI_SECUREAPICALL_API_URL to the URL'}),
                "data": ('STRING', {'default': '{"data": "some_data"}'}),
                "aws_access_key_id": ("STRING", {'default': '', 'tooltip': 'The AWS Access Key ID (USE $ENV.AWS_ACCESS_KEY_ID) and set COMFYUI_SECUREAPICALL_AWS_ACCESS_KEY_ID to the ID'}),
                "aws_secret_access_key": ("STRING", {'default': '', 'tooltip': 'The AWS Secret Access Key (USE $ENV.AWS_SECRET_ACCESS_KEY) and set COMFYUI_SECUREAPICALL_AWS_SECRET_ACCESS_KEY to the Key'}),
                "region_name": ("STRING", {'default': '', 'tooltip': 'The AWS Region Name (USE $ENV.AWS_REGION_NAME) and set COMFYUI_SECUREAPICALL_AWS_REGION_NAME to the Region'}),
            }
        }

    FUNCTION = 'hook'
    OUTPUT_NODE = True
    RETURN_TYPES = tuple()
    CATEGORY = "notifications"

    def resolve_env_var(self, value: str, var_name: str) -> str:
        #Resolve environment variables with validation
        if not value.startswith("$ENV."):
            return value
            
        env_name = value.removeprefix("$ENV.")
        if not env_name.replace("_", "").isalnum():
            raise ValueError("Environment variable names must only contain letters, numbers, and underscores")
            
        env_var = f"COMFYUI_SECUREAPICALL_{env_name}"
        resolved_value = os.getenv(env_var)
        if not resolved_value:
            raise ValueError(f"Environment Variable {env_var} is not set")
            
        return resolved_value

    def hook(self, any, api_url, aws_access_key_id, aws_secret_access_key, region_name, data, full_comfyui_info, timeout, verify_ssl):
        # Validate URL before proceeding
        url_error = self.validate_url(api_url)
        if url_error:
            raise ValueError(f"Invalid API URL: {url_error}")

        # Get the payload from the data string
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON data provided")

        # Add ComfyUI execution information to the payload
        current_queue = server.PromptServer.instance.prompt_queue.get_current_queue()

        # The response is a massive object (containing all nodes and workflow info) -- we only want the prompt_id for tracking, but if full_comfyui_info is true, we want to include the entire object
        prompt_id = current_queue[0][0][1]
        payload.update({"comfyui_execution_info": {"prompt_id": prompt_id}})
        if full_comfyui_info:
            payload.update({"comfyui_info": {"full_comfyui_info": current_queue}})

        # Resolve environment variables
        api_url = self.resolve_env_var(api_url, "api_url")
        aws_access_key_id = self.resolve_env_var(aws_access_key_id, "aws_access_key_id")
        aws_secret_access_key = self.resolve_env_var(aws_secret_access_key, "aws_secret_access_key")

        # Configure AWS credentials
        session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        credentials = session.get_credentials()

        api_url = api_url
        # Prepare the request
        request = AWSRequest(
            method='POST',
            url=api_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        # Sign the request with SigV4
        SigV4Auth(credentials, 'execute-api', session.region_name).add_auth(request)

        # Send the signed request
        res = requests.post(
            api_url,
            data=request.data,
            headers=dict(request.headers)
        )

        res.raise_for_status()
        return (0, )
