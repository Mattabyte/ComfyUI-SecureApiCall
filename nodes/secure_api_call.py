import requests
import json

from .util import ComfyAnyType

class SecureApiCall:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any": (ComfyAnyType("*"), {}),
                "api_url": ("STRING", {'default': 'https://localhost:9001/'}),
                "json_body": ('STRING', {'default': '{"body": "json_body_data"}'}),
                "api_auth": ("STRING", {'default': 'x-api-key'}),
                "timeout": ('FLOAT', {'default': 3, 'min': 0, 'max': 60}),
                "verify_ssl": ("BOOLEAN", {"default": True}),
            },
        }

    FUNCTION = 'hook'
    OUTPUT_NODE = True
    RETURN_TYPES = tuple()
    CATEGORY = "notifications"

    def hook(self, any, api_url, api_auth,json_body, timeout, verify_ssl):
        payload = json.loads(json_body)
        res = requests.post(api_url, json=payload, timeout=timeout, headers={"Content-Type": "application/json", "x-api-key": api_auth}, verify=verify_ssl)
        res.raise_for_status()
        return (0, )
