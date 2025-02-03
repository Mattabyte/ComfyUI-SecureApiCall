import requests
import json
import server
import os
import urllib.parse
from typing import Optional

from .util import ComfyAnyType

class SecureApiCall:
    ALLOWED_SCHEMES = {'https', 'http'}
    
    @staticmethod
    def validate_url(url: str) -> Optional[str]:
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in SecureApiCall.ALLOWED_SCHEMES:
                return f"URL scheme must be one of: {', '.join(SecureApiCall.ALLOWED_SCHEMES)}"
            return None
        except Exception:
            return "Invalid URL format"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (ComfyAnyType("*"), {}),
                "api_url": ("STRING", {'default': 'https://localhost:9001/', 'tooltip': 'The API Url (USE $ENV.API_URL) and set CSAPI_API_URL to the URL'}),
                "data": ('STRING', {'default': '{"data": "some_data"}'}),
                "full_comfyui_info": ("BOOLEAN", {"default": True}),
                "api_auth": ("STRING", {'default': 'x-api-key', 'tooltip': 'The API key to use for authentication (USE $ENV.API_KEY) and set CSAPI_API_KEY to the URL'}),
                "timeout": ('FLOAT', {'default': 3, 'min': 0, 'max': 60}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
            },
        }

    FUNCTION = 'hook'
    OUTPUT_NODE = True
    RETURN_TYPES = tuple()
    CATEGORY = "SecureApiCall"

    def resolve_env_var(self, value: str, var_name: str) -> str:
        #Resolve environment variables with validation
        if not value.startswith("$ENV."):
            return value
            
        env_name = value.removeprefix("$ENV.")
        if not env_name.replace("_", "").isalnum():
            raise ValueError("Environment variable names must only contain letters, numbers, and underscores")
            
        env_var = f"CSAPI_{env_name}"
        resolved_value = os.getenv(env_var)
        if not resolved_value:
            raise ValueError(f"Environment Variable {env_var} is not set")
            
        return resolved_value

    def hook(self, any, api_url, api_auth, data, full_comfyui_info, timeout, verify_ssl):
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


        # Resolve any environment variables in the api_url, api_auth fields -- Only allow COMFYUI_SECUREAPICALL_ prefixed variables
        api_url = self.resolve_env_var(api_url, "api_url")
        api_auth = self.resolve_env_var(api_auth, "api_auth")

        # Validate URL before proceeding
        url_error = self.validate_url(api_url)
        if url_error:
            raise ValueError(f"Invalid API URL: {url_error}")
            
        # Send the payload to the API
        res = requests.post(
            api_url, 
            json=payload, 
            timeout=timeout, 
            headers={"Content-Type": "application/json", "x-api-key": api_auth}, 
            verify=verify_ssl
        )
        res.raise_for_status()
        return (0, )
