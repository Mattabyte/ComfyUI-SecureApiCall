from .nodes.secure_api_call import SecureApiCall
from .nodes.secure_api_call_aws import SecureApiCallAws
from .nodes.save_video_files_s3 import SaveVideoFilesS3
from .nodes.save_latent_s3 import SaveLatentToS3
NODE_CLASS_MAPPINGS = {
    "SecureAPI-SecureAPI": SecureApiCall,
    "SecureAPI-SecureAPI-AWS": SecureApiCallAws,
    "SaveVideoFilesS3": SaveVideoFilesS3,
    "SaveLatentToS3": SaveLatentToS3
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SecureAPI-SecureAPI": "Secure API Call",
    "SecureAPI-SecureAPI-AWS": "Secure API Call (AWS)",
    "SaveVideoFilesS3": "Save Video Files to S3",
    "SaveLatentToS3": "Save Latent to S3"
}

