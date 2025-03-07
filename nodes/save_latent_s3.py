import os
import json
import torch
import comfy.utils

from ..client_s3 import get_s3_instance
from folder_paths import get_output_directory, get_save_image_path
import folder_paths
from comfy.cli_args import args

S3_INSTANCE = get_s3_instance()

class SaveLatentToS3:
    def __init__(self):
        self.output_dir = get_output_directory()
        self.s3_output_dir = os.getenv("S3_OUTPUT_DIR")
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "samples": ("LATENT", ),
                              "filename_prefix": ("STRING", {"default": "latents/ComfyUI"})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("latent_file_path",)
    FUNCTION = "save"

    OUTPUT_NODE = True

    CATEGORY = "SaveLatentToS3"

    def save(self, samples, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        full_output_folder, filename, counter, subfolder, filename_prefix = get_save_image_path(filename_prefix, self.output_dir)
        # support save metadata for latent sharing
        prompt_info = ""
        if prompt is not None:
            prompt_info = json.dumps(prompt)

        metadata = None
        if not args.disable_metadata:
            metadata = {"prompt": prompt_info}
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata[x] = json.dumps(extra_pnginfo[x])

        file = f"{filename}_{counter:05}.latent"
        file_path = os.path.join(full_output_folder, file)

        output = {}
        output["latent_tensor"] = samples["samples"]
        output["latent_format_version_0"] = torch.tensor([])

        comfy.utils.save_torch_file(output, file_path, metadata=metadata)

        # Upload to S3
        full_output_folder_s3, filename_s3, counter_s3, _, filename_prefix_s3 = S3_INSTANCE.get_save_path(filename_prefix)
        s3_file = f"{filename_s3}_{counter_s3:05}.latent"
        s3_path = os.path.join(full_output_folder_s3, s3_file)
        s3_file_path = S3_INSTANCE.upload_file(file_path, s3_path)

        return (s3_file_path,)
