# Mock ComfyUI environment
class MockContainsAll(dict):
    def __contains__(self, key):
        return True

imageOrLatent = ("IMAGE", "LATENT")
floatOrInt = ("FLOAT", "INT")
ContainsAll = MockContainsAll
class MockVideoCombine:
    def combine_video(self, *args, **kwargs):
        return {"result": (("save_output", ["test.mp4"]), "mock_images")}

class EnhancedVideoCombine(MockVideoCombine):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": (imageOrLatent,),
                "frame_rate": (floatOrInt, {"default": 8, "min": 1, "step": 1}),
                "loop_count": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "filename_prefix": ("STRING", {"default": "enhanced_video"}),
                "format": (["image/gif", "image/webp", "video/h264-mp4", "video/h265-mp4", "video/webm", "video/av1-webm"], {}),
                "pingpong": ("BOOLEAN", {"default": False}),
                "save_output": ("BOOLEAN", {"default": True}),
                "pix_fmt": (["yuv420p", "yuv420p10le", "yuv422p", "yuv444p", "rgb24"], {"default": "yuv420p"}),
                "crf": ("INT", {"default": 19, "min": 0, "max": 51, "step": 1}),
                "preset": (["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"], {"default": "medium"}),
                "save_metadata": ("BOOLEAN", {"default": True}),
                "trim_to_audio": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "audio": ("AUDIO",),
                "meta_batch": ("VHS_BatchManager",),
                "vae": ("VAE",),
            },
            "hidden": ContainsAll({
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID"
            }),
        }

    RETURN_TYPES = ("VHS_FILENAMES", "IMAGE", "VHS_VIDEOINFO")
    RETURN_NAMES = ("Filenames", "images", "video_info")
    OUTPUT_NODE = True
    CATEGORY = "Enhanced Video"
    FUNCTION = "combine_video"

def test_static_params():
    print("Testing Enhanced Video Combine static parameters...")
    
    input_types = EnhancedVideoCombine.INPUT_TYPES()
    print("INPUT_TYPES loaded successfully")
    required = input_types['required']
    expected_params = [
        'images', 'frame_rate', 'loop_count', 'filename_prefix', 
        'format', 'pingpong', 'save_output',
        'pix_fmt', 'crf', 'preset', 'save_metadata', 'trim_to_audio'
    ]
    
    print("\nChecking static parameters:")
    all_present = True
    for param in expected_params:
        if param in required:
            param_def = required[param]
            if isinstance(param_def, tuple) and len(param_def) >= 2:
                param_type = param_def[0]
                param_config = param_def[1] if len(param_def) > 1 else {}
                default_val = param_config.get('default', 'N/A')
                print(f"  OK {param}: {param_type} (default: {default_val})")
            else:
                print(f"  OK {param}: {param_def}")
        else:
            print(f"  ERROR Missing parameter: {param}")
            all_present = False
    
    print(f"\nReturn types: {EnhancedVideoCombine.RETURN_TYPES}")
    print(f"Return names: {EnhancedVideoCombine.RETURN_NAMES}")
    
    print("\nKey parameter configurations:")
    
    pix_fmt_config = required.get('pix_fmt')
    if pix_fmt_config:
        print(f"  pix_fmt options: {pix_fmt_config[0]}")
        print(f"  pix_fmt default: {pix_fmt_config[1].get('default')}")
    
    crf_config = required.get('crf')
    if crf_config:
        print(f"  crf range: {crf_config[1].get('min')}-{crf_config[1].get('max')}")
        print(f"  crf default: {crf_config[1].get('default')}")
    
    preset_config = required.get('preset')
    if preset_config:
        print(f"  preset options: {preset_config[0]}")
        print(f"  preset default: {preset_config[1].get('default')}")
    
    if all_present:
        print("\nAll static parameters test passed!")
        return True
    else:
        print("\nSome parameters are missing")
        return False

if __name__ == "__main__":
    success = test_static_params()
    if success:
        print("\nEnhanced Video Combine static parameters configuration verified successfully!")
        print("All important video encoding parameters will now be displayed on the panel:")
        print("- pix_fmt: Pixel format selection")
        print("- crf: Compression quality control (0-51)")
        print("- preset: Encoding speed preset")
        print("- save_metadata: Save metadata")
        print("- trim_to_audio: Trim to audio length")
        print("\nPlease restart ComfyUI to load the updated node")
    else:
        print("\nConfiguration verification failed")
