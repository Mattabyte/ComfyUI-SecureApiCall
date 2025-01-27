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
                "api_auth": ("STRING", {'default': 'x-api-key'}),
                "timeout": ('FLOAT', {'default': 3, 'min': 0, 'max': 60}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
            },
        }

    FUNCTION = 'hook'
    OUTPUT_NODE = True
    RETURN_TYPES = tuple()
    CATEGORY = "notifications"

    def hook(self, any, api_url, api_auth, data, timeout, verify_ssl):
        # Get the payload from the data string
        payload = json.loads(data)
        # Add ComfyUI execution information to the payload
        current_queue = server.PromptServer.instance.prompt_queue.get_current_queue()
        # The response is a massive object (containing all nodes and workflow info) -- we only want the prompt_id for tracking
        prompt_id = current_queue[0][0][1]
        payload.update({"comfyui_execution_info": {"prompt_id": prompt_id}})

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
