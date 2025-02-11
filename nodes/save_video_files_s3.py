import os
from PIL import Image

from ..client_s3 import get_s3_instance
S3_INSTANCE = get_s3_instance()


class SaveVideoFilesS3:
    def __init__(self):
        self.s3_output_dir = os.getenv("S3_OUTPUT_DIR")
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "filename_prefix": ("STRING", {"default": "VideoFiles"}),
            "convert_any_png_to_jpg": ("BOOLEAN", {"default": False}),
            "filenames": ("VHS_FILENAMES", )
            }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_video_paths",)
    FUNCTION = "save_video_files"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    CATEGORY = "SaveVideoFilesS3"

    def save_video_files(self, filenames, filename_prefix="VideoFiles", convert_any_png_to_jpg=False):
        filename_prefix += self.prefix_append
        local_files = filenames[1]
        full_output_folder, filename, counter, _, filename_prefix = S3_INSTANCE.get_save_path(filename_prefix)
        s3_video_paths = list()
        
        for path in local_files:
            ext = path.split(".")[-1]
            # If conversion is enabled and this is a png file, convert it to jpg.
            if convert_any_png_to_jpg and ext.lower() == "png":
                from PIL import Image
                import tempfile
                # Open and convert the image.
                with Image.open(path) as img:
                    rgb_img = img.convert("RGB")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp_file_path = tmp.name
                        rgb_img.save(tmp_file_path, format="JPEG")
                # Update extension and file name to reflect the conversion.
                ext = "jpg"
                file_name = f"{filename}_{counter:05}_.{ext}"
                s3_path = os.path.join(full_output_folder, file_name)
                file_path = S3_INSTANCE.upload_file(tmp_file_path, s3_path)
                os.unlink(tmp_file_path)  # Remove the temporary file.
            else:
                file_name = f"{filename}_{counter:05}_.{ext}"
                s3_path = os.path.join(full_output_folder, file_name)
                file_path = S3_INSTANCE.upload_file(path, s3_path)
            
            s3_video_paths.append(file_path)
            counter += 1  # Increment counter for each file.
        
        return (s3_video_paths,)
