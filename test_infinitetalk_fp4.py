# Test InfiniteTalk with FP4 quantization and sageattn_3_fp4
# Parameters: 81 frames, 640x720, fp4, sageattn_3_fp4, 6 steps, shift 7, 40 blocks

import sys
import os

# Add genesis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'genesis'))

from apps.wanvideo_gradio_app import WanVideoWorkflow
from PIL import Image
import torch

print("=" * 80)
print("InfiniteTalk FP4 Test")
print("=" * 80)
print()

# Test parameters
test_params = {
    "image_path": r"D:\rh推广项目\工作流及图形\1ecf8fdfbb57ef8ebb1cbec5973d5cc732c1a12cda6b2e71ac46a1aa4af40548.jpg",
    "width": 640,
    "height": 720,
    "num_frames": 81,
    "steps": 6,
    "shift": 7,
    "blocks_to_swap": 40,
    "quantization": "fp4_experimental",
    "attention_mode": "sageattn_3_fp4",
    "positive_prompt": "A beautiful woman smiling",
    "negative_prompt": "",
}

print("Test Configuration:")
print(f"  Image: {test_params['image_path']}")
print(f"  Resolution: {test_params['width']}x{test_params['height']}")
print(f"  Frames: {test_params['num_frames']}")
print(f"  Steps: {test_params['steps']}")
print(f"  Shift: {test_params['shift']}")
print(f"  Blocks to Swap: {test_params['blocks_to_swap']}")
print(f"  Quantization: {test_params['quantization']}")
print(f"  Attention Mode: {test_params['attention_mode']}")
print()

# Check if image exists
if not os.path.exists(test_params['image_path']):
    print(f"ERROR: Image not found: {test_params['image_path']}")
    sys.exit(1)

print("Loading image...")
input_image = Image.open(test_params['image_path'])
print(f"Image loaded: {input_image.size}")
print()

# Initialize workflow
print("Initializing WanVideoWorkflow...")
workflow = WanVideoWorkflow()
print("Workflow initialized")
print()

# Progress callback
def progress_callback(value, desc):
    print(f"[{value*100:.1f}%] {desc}")

try:
    print("Starting generation...")
    print("-" * 80)
    
    video_path, video_array, metadata = workflow.generate_image_to_video(
        input_image=input_image,
        positive_prompt=test_params['positive_prompt'],
        negative_prompt=test_params['negative_prompt'],
        model_name="Wan2_IceCannon_t2v2.1_nsfw_RCM_Lab_4step.safetensors",
        vae_name="Wan2_1_VAE_bf16.safetensors",
        t5_model="models_t5_umt5-xxl-enc-fp8_fully_uncensored.safetensors",
        width=test_params['width'],
        height=test_params['height'],
        num_frames=test_params['num_frames'],
        steps=test_params['steps'],
        cfg=7.0,
        shift=test_params['shift'],
        seed=-1,
        scheduler="euler",
        denoise_strength=1.0,
        base_precision="disabled",
        quantization=test_params['quantization'],
        attention_mode=test_params['attention_mode'],
        mode="InfiniteTalk",
        audio_file=None,  # No audio
        keep_proportion="crop",
        crop_position="center",
        upscale_method="lanczos",
        colormatch="disabled",
        fps=16,
        output_format="mp4",
        # LoRA parameters
        lora_enabled=False,
        lora_name="",
        lora_strength=1.0,
        # Optimization parameters
        compile_enabled=False,
        compile_backend="inductor",
        block_swap_enabled=True,
        # VRAM Management parameters
        auto_hardware_tuning=True,
        vram_threshold_percent=50.0,
        blocks_to_swap=test_params['blocks_to_swap'],
        enable_cuda_optimization=True,
        enable_dram_optimization=True,
        num_cuda_streams=8,
        bandwidth_target=0.8,
        offload_txt_emb=False,
        offload_img_emb=False,
        vace_blocks_to_swap=0,
        vram_debug_mode=False,
        progress_callback=progress_callback
    )
    
    print("-" * 80)
    print()
    print("=" * 80)
    print("Generation Complete!")
    print("=" * 80)
    print(f"Video saved to: {video_path}")
    print(f"Video shape: {video_array.shape if video_array is not None else 'N/A'}")
    print()
    print("Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print()
    print("Test PASSED ✅")
    
except Exception as e:
    print()
    print("=" * 80)
    print("Generation Failed!")
    print("=" * 80)
    print(f"Error: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Test FAILED ❌")
    sys.exit(1)
