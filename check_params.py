#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 I2V 生成按钮的参数数量
"""

# 按钮 inputs 列表中的参数
inputs_list = [
    "input_image",           # 1
    "i2v_mode",              # 2
    "i2v_positive_prompt",   # 3
    "i2v_negative_prompt",   # 4
    "i2v_model_name",        # 5
    "i2v_vae_name",          # 6
    "i2v_t5_model",          # 7
    "i2v_width",             # 8
    "i2v_height",            # 9
    "i2v_num_frames",        # 10
    "i2v_steps",             # 11
    "i2v_cfg",               # 12
    "i2v_shift",             # 13
    "i2v_seed",              # 14
    "i2v_scheduler",         # 15
    "i2v_denoise",           # 16
    "i2v_base_precision",    # 17
    "i2v_quantization",      # 18
    "i2v_attention_mode",    # 19
    "audio_file",            # 20
    "frame_window_size",     # 21
    "motion_frame",          # 22
    "wav2vec_precision",     # 23
    "wav2vec_device",        # 24
    "keep_proportion",       # 25
    "crop_position",         # 26
    "upscale_method",        # 27
    "pose_images",           # 28
    "face_images",           # 29
    "pose_strength",         # 30
    "face_strength",         # 31
    "colormatch",            # 32
    "i2v_fps",               # 33
]

# 函数参数解包
unpack_params = [
    "input_image",           # 1
    "mode",                  # 2
    "positive_prompt",       # 3
    "negative_prompt",       # 4
    "model_name",            # 5
    "vae_name",              # 6
    "t5_model",              # 7
    "width",                 # 8
    "height",                # 9
    "num_frames",            # 10
    "steps",                 # 11
    "cfg",                   # 12
    "shift",                 # 13
    "seed",                  # 14
    "scheduler",             # 15
    "denoise",               # 16
    "base_precision",        # 17
    "quantization",          # 18
    "attention_mode",        # 19
    "audio_file",            # 20
    "frame_window_size",     # 21
    "motion_frame",          # 22
    "wav2vec_precision",     # 23
    "wav2vec_device",        # 24
    "keep_proportion",       # 25
    "crop_position",         # 26
    "upscale_method",        # 27
    "pose_images",           # 28
    "face_images",           # 29
    "pose_strength",         # 30
    "face_strength",         # 31
    "colormatch",            # 32
    "fps",                   # 33
]

print("=" * 80)
print("参数数量检查")
print("=" * 80)
print(f"\n按钮 inputs 列表参数数量: {len(inputs_list)}")
print(f"函数解包参数数量: {len(unpack_params)}")

if len(inputs_list) == len(unpack_params):
    print("\n✅ 参数数量匹配！")
else:
    print(f"\n❌ 参数数量不匹配！差异: {len(inputs_list) - len(unpack_params)}")

print("\n" + "=" * 80)
print("参数对照表")
print("=" * 80)

for i, (inp, unp) in enumerate(zip(inputs_list, unpack_params), 1):
    print(f"{i:2d}. {inp:25s} → {unp}")

print("\n" + "=" * 80)
