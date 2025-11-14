"""
测试InfiniteTalk节点是否正常工作
"""

import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

print("[INFO] Testing InfiniteTalk nodes...")

# Import necessary modules
import os
os.environ['COMFYUI_PATH'] = str(project_root)

sys.path.insert(0, str(project_root / "genesis"))

# Import triton stub
from genesis.utils import triton_ops_stub

# Import genesis components
from genesis.compat import comfy_stub
from genesis.core import folder_paths_ext

# Setup ComfyUI-WanVideoWrapper
import importlib.util
wrapper_path = project_root / "genesis" / "custom_nodes" / "Comfyui" / "ComfyUI-WanVideoWrapper"

print(f"[DEBUG] Wrapper path: {wrapper_path}")

# Load nodes
spec = importlib.util.spec_from_file_location("ComfyUI-WanVideoWrapper", wrapper_path / "__init__.py")
wrapper_module = importlib.util.module_from_spec(spec)
sys.modules["ComfyUI-WanVideoWrapper"] = wrapper_module
spec.loader.exec_module(wrapper_module)

NODE_CLASS_MAPPINGS = wrapper_module.NODE_CLASS_MAPPINGS

print("\n[TEST 1] Checking if LoadCLIPVision exists...")
if 'LoadCLIPVision' in NODE_CLASS_MAPPINGS:
    print("✓ LoadCLIPVision found")
else:
    print("✗ LoadCLIPVision NOT found")
    print(f"Available nodes: {list(NODE_CLASS_MAPPINGS.keys())[:10]}...")

print("\n[TEST 2] Checking if WanVideoClipVisionEncode exists...")
if 'WanVideoClipVisionEncode' in NODE_CLASS_MAPPINGS:
    print("✓ WanVideoClipVisionEncode found")
else:
    print("✗ WanVideoClipVisionEncode NOT found")

print("\n[TEST 3] Checking if WanVideoImageToVideoMultiTalk exists...")
if 'WanVideoImageToVideoMultiTalk' in NODE_CLASS_MAPPINGS:
    print("✓ WanVideoImageToVideoMultiTalk found")
else:
    print("✗ WanVideoImageToVideoMultiTalk NOT found")

print("\n[TEST 4] Checking CLIP Vision model file...")
clip_vision_path = project_root / "genesis" / "models" / "clip_vision" / "sigclip_vision_patch14_384.safetensors"
if clip_vision_path.exists():
    print(f"✓ CLIP Vision model found at: {clip_vision_path}")
else:
    print(f"✗ CLIP Vision model NOT found at: {clip_vision_path}")
    # Check alternative locations
    alt_paths = [
        project_root / "models" / "clip_vision" / "sigclip_vision_patch14_384.safetensors",
        Path("models/clip_vision/sigclip_vision_patch14_384.safetensors"),
    ]
    for alt_path in alt_paths:
        if alt_path.exists():
            print(f"  Found at alternative location: {alt_path}")
            break

print("\n[TEST 5] Trying to instantiate LoadCLIPVision...")
try:
    clip_vision_loader = NODE_CLASS_MAPPINGS['LoadCLIPVision']()
    print("✓ LoadCLIPVision instantiated successfully")
    
    print("\n[TEST 6] Trying to load CLIP Vision model...")
    try:
        result = clip_vision_loader.load_model(
            model_name="sigclip_vision_patch14_384.safetensors"
        )
        print("✓ CLIP Vision model loaded successfully")
        print(f"  Result type: {type(result)}")
        print(f"  Result length: {len(result)}")
    except Exception as e:
        print(f"✗ Failed to load CLIP Vision model: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"✗ Failed to instantiate LoadCLIPVision: {e}")
    import traceback
    traceback.print_exc()

print("\n[DONE] Test completed")
