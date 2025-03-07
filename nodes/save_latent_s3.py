import os

from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()

class SaveLatentToS3:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "samples": ("LATENT", ),
                              "filename_prefix": ("STRING", {"default": "latents/ComfyUI"})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }
    RETURN_TYPES = ("STRING")
    RETURN_NAMES = ("latent_file_path",)
    FUNCTION = "save"

    OUTPUT_NODE = True

    CATEGORY = "SaveVideoFilesS3"

    def save(self, samples, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)
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

        file = f"{filename}_.latent"

        results: list[FileLocator] = []
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": "output"
        })

        file = os.path.join(full_output_folder, file)

        output = {}
        output["latent_tensor"] = samples["samples"]
        output["latent_format_version_0"] = torch.tensor([])

        comfy.utils.save_torch_file(output, file, metadata=metadata)

        #Upload to S3
        full_output_folder, filename, counter, _, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix)
        s3_path = os.path.join(full_output_folder, file)
        file_path = S3_INSTANCE.upload_file(file, s3_path)


        return {file_path}
