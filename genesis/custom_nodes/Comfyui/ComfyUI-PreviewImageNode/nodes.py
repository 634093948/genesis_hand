"""
ComfyUI Preview Image Node (Standalone)
Author: eddy
Description: Standalone version of ComfyUI's PreviewImage node
"""

import os
import json
import random
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

try:
    import folder_paths
    FOLDER_PATHS_AVAILABLE = True
except ImportError:
    FOLDER_PATHS_AVAILABLE = False
    import tempfile
    class folder_paths:
        @staticmethod
        def get_temp_directory():
            return tempfile.gettempdir()
        
        @staticmethod
        def get_output_directory():
            return os.path.join(os.path.dirname(__file__), "output")
        
        @staticmethod
        def get_save_image_path(filename_prefix, output_dir, width, height):
            counter = 1
            os.makedirs(output_dir, exist_ok=True)
            return output_dir, filename_prefix, counter, "", filename_prefix

try:
    from comfy.cli_args import args
except ImportError:
    class args:
        disable_metadata = False


class SaveImage:
    """
    Base class for saving images
    """
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory() if FOLDER_PATHS_AVAILABLE else "./output"
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {
                    "default": "ComfyUI",
                    "tooltip": "The prefix for the file to save."
                })
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"
    DESCRIPTION = "Saves the input images to your ComfyUI output directory."

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )
        
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}, "result": (images,)}


class PreviewImage(SaveImage):
    """
    Standalone PreviewImage node
    Displays images in the UI without saving to output directory
    """
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory() if FOLDER_PATHS_AVAILABLE else tempfile.gettempdir()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview in the UI"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"
    DESCRIPTION = "Preview images in the ComfyUI interface. Images are saved to temp directory and displayed in the node."


NODE_CLASS_MAPPINGS = {
    "PreviewImageStandalone": PreviewImage,
    "SaveImageStandalone": SaveImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PreviewImageStandalone": "Preview Image (Standalone)",
    "SaveImageStandalone": "Save Image (Standalone)",
}
