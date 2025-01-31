from .nodes.secure_api_call import SecureApiCall
from .nodes.secure_api_call_aws import SecureApiCallAws

NODE_CLASS_MAPPINGS = {
    "SecureAPI-SecureAPI": SecureApiCall,
    "SecureAPI-SecureAPI-AWS": SecureApiCallAws
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SecureAPI-SecureAPI": "Secure API Call",
    "SecureAPI-SecureAPI-AWS": "Secure API Call (AWS)"
}

