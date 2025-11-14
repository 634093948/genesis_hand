import os
import json
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence, ImageDraw
import folder_paths
import node_helpers

class ImageCompositor:
    """
    Image Compositor - Background + Layers Editor
    Upload a background image, then add and position multiple layers on it
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = []
        if os.path.exists(input_dir):
            files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
            files = folder_paths.filter_files_content_types(files, ["image"])
        
        return {
            "required": {
                "background": (sorted(files) if files else [""], {"image_upload": True}),
            },
            "optional": {
                "layers_data": ("STRING", {
                    "default": "[]",
                    "multiline": True,
                    "dynamicPrompts": False
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("composite", "mask", "layer_info")
    FUNCTION = "compose_image"
    CATEGORY = "image"
    
    def compose_image(self, background, layers_data="[]", output_width=0, output_height=0):
        if not background:
            empty_img = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
            return (empty_img, empty_mask, "No background")
        
        try:
            bg_path = folder_paths.get_annotated_filepath(background)
            bg_img = node_helpers.pillow(Image.open, bg_path)
            bg_img = node_helpers.pillow(ImageOps.exif_transpose, bg_img)
            bg_img = bg_img.convert("RGBA")
            bg_w, bg_h = bg_img.size
            
            # Use background original size if output size is 0
            final_width = bg_w if output_width <= 0 else output_width
            final_height = bg_h if output_height <= 0 else output_height
            
            if (bg_w, bg_h) != (final_width, final_height):
                bg_img = bg_img.resize((final_width, final_height), Image.LANCZOS)
            
            output_width = final_width
            output_height = final_height
        except Exception as e:
            print(f"Error loading background: {e}")
            empty_img = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
            return (empty_img, empty_mask, f"Error: {e}")
        
        try:
            layers_list = json.loads(layers_data)
        except:
            layers_list = []
        
        canvas = bg_img.copy()
        mask_canvas = Image.new('L', (output_width, output_height), 0)
        
        for layer_info in layers_list:
            if not isinstance(layer_info, dict):
                continue
            
            layer_name = layer_info.get("name", "")
            if not layer_name:
                continue
            
            x = int(layer_info.get("x", 0))
            y = int(layer_info.get("y", 0))
            req_w = layer_info.get("width", None)
            req_h = layer_info.get("height", None)
            opacity = float(layer_info.get("opacity", 1.0))
            visible = layer_info.get("visible", True)
            
            if not visible:
                continue
            
            try:
                layer_path = folder_paths.get_annotated_filepath(layer_name)
                layer_img = node_helpers.pillow(Image.open, layer_path)
                layer_img = node_helpers.pillow(ImageOps.exif_transpose, layer_img)
                layer_img = layer_img.convert("RGBA")
                lw, lh = layer_img.size
                if req_w is None and req_h is None:
                    width, height = lw, lh
                elif req_w is not None and req_h is None:
                    width = int(req_w)
                    height = max(1, int(lh * (width / lw)))
                elif req_w is None and req_h is not None:
                    height = int(req_h)
                    width = max(1, int(lw * (height / lh)))
                else:
                    width = int(req_w)
                    height = int(req_h)
                if (lw, lh) != (width, height):
                    layer_img = layer_img.resize((width, height), Image.LANCZOS)
                
                if opacity < 1.0:
                    alpha = layer_img.split()[3]
                    alpha = alpha.point(lambda p: int(p * opacity))
                    layer_img.putalpha(alpha)
                
                canvas.paste(layer_img, (x, y), layer_img)
                
                layer_mask = Image.new('L', (width, height), 255)
                mask_canvas.paste(layer_mask, (x, y))
                
            except Exception as e:
                print(f"Error loading layer {layer_name}: {e}")
                continue
        
        canvas_rgb = canvas.convert("RGB")
        image_array = np.array(canvas_rgb).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_array)[None,]
        
        mask_array = np.array(mask_canvas).astype(np.float32) / 255.0
        mask_tensor = torch.from_numpy(mask_array)[None,]
        
        layer_info_str = json.dumps({
            "background": background,
            "background_original_size": f"{bg_w}x{bg_h}",
            "output_size": f"{output_width}x{output_height}",
            "layers_count": len(layers_list)
        }, indent=2)
        
        return (image_tensor, mask_tensor, layer_info_str)


class LayerUploader:
    """
    Upload images to be used as layers
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = []
        if os.path.exists(input_dir):
            files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
            files = folder_paths.filter_files_content_types(files, ["image"])
        
        return {
            "required": {
                "mode": (["single", "batch"], {"default": "single"}),
            },
            "optional": {
                "image": (sorted(files) if files else [""], {"image_upload": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "filename")
    FUNCTION = "upload_image"
    CATEGORY = "image"
    
    def upload_image(self, mode="single", image=None):
        if not image:
            empty_img = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
            empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
            return (empty_img, empty_mask, "")
        
        image_path = folder_paths.get_annotated_filepath(image)
        img = node_helpers.pillow(Image.open, image_path)
        
        output_images = []
        output_masks = []
        
        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)
            
            if i.mode == 'I':
                i = i.point(lambda x: x * (1 / 255))
            
            image_rgb = i.convert("RGB")
            image_array = np.array(image_rgb).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]
            
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((image_rgb.size[1], image_rgb.size[0]), dtype=torch.float32)
            
            output_images.append(image_tensor)
            output_masks.append(mask.unsqueeze(0))
            
            if mode == "single":
                break
        
        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]
        
        return (output_image, output_mask, image)


NODE_CLASS_MAPPINGS = {
    "ImageCompositor": ImageCompositor,
    "LayerUploader": LayerUploader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageCompositor": "Image Compositor 🎨",
    "LayerUploader": "Layer Uploader 📤",
}
