import requests
import json
import server

from .util import ComfyAnyType

class SecureApiCall:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (ComfyAnyType("*"), {}),
                "api_url": ("STRING", {'default': 'https://localhost:9001/'}),
                "data": ('STRING', {'default': '{"data": "some_data"}'}),
                "full_comfyui_info": ("BOOLEAN", {"default": True}),
                "api_auth": ("STRING", {'default': 'x-api-key'}),
                "timeout": ('FLOAT', {'default': 3, 'min': 0, 'max': 60}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
            },
        }

    FUNCTION = 'hook'
    OUTPUT_NODE = True
    RETURN_TYPES = tuple()
    CATEGORY = "notifications"

    def hook(self, any, api_url, api_auth, data, full_comfyui_info, timeout, verify_ssl):
        # Get the payload from the data string
        payload = json.loads(data)
        # Add ComfyUI execution information to the payload
        current_queue = server.PromptServer.instance.prompt_queue.get_current_queue()

        # The response is a massive object (containing all nodes and workflow info) -- we only want the prompt_id for tracking, but if full_comfyui_info is true, we want to include the entire object
        prompt_id = current_queue[0][0][1]
        payload.update({"comfyui_execution_info": {"prompt_id": prompt_id}})
        if include_full_comfyui_info:
            payload.update({"comfyui_info": {"full_comfyui_info": current_queue}})


        # Resolve any environment variables in the api_url, api_auth fields -- If the variable is not set, change the value to 'NOT_SET'
        if api_url.startswith("$ENV."):
            api_url = os.getenv(api_url.removeprefix("$ENV.")) or 'NOT_SET'
        if api_auth.startswith("$ENV."):
            api_auth = os.getenv(api_auth.removeprefix("$ENV.")) or 'NOT_SET'

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
