# UI 优化补丁
# 这个文件包含所有 UI 优化的代码片段
# 可以逐步应用到 wanvideo_gradio_app.py

import gradio as gr

# ============================================================================
# 1. 宽高比保持功能
# ============================================================================

def create_aspect_ratio_controls():
    """创建带宽高比锁定的尺寸控制"""
    
    with gr.Group():
        gr.Markdown("### 📐 视频尺寸")
        
        with gr.Row():
            i2v_width = gr.Slider(
                64, 2048, value=832, step=16,
                label="宽度 (Width)",
                info="必须是16的倍数"
            )
            i2v_height = gr.Slider(
                64, 2048, value=480, step=16,
                label="高度 (Height)",
                info="必须是16的倍数"
            )
            lock_aspect_ratio = gr.Checkbox(
                value=True,
                label="🔒 锁定宽高比",
                info="保持 832:480 比例"
            )
        
        with gr.Row():
            i2v_num_frames = gr.Slider(
                1, 241, value=81, step=4,
                label="帧数 (Frames)",
                info="必须是4的倍数"
            )
            i2v_fps = gr.Slider(
                8, 60, value=25, step=1,
                label="帧率 (FPS)",
                info="InfiniteTalk推荐25"
            )
    
    # 宽高比计算函数
    def on_width_change(width, height, lock):
        """宽度改变时，自动调整高度"""
        if not lock:
            return gr.update()
        
        # 计算当前宽高比（基于初始值 832:480）
        aspect_ratio = 832 / 480  # 1.733...
        new_height = round(width / aspect_ratio / 16) * 16
        new_height = max(64, min(2048, new_height))  # 限制范围
        
        return gr.update(value=new_height)
    
    def on_height_change(width, height, lock):
        """高度改变时，自动调整宽度"""
        if not lock:
            return gr.update()
        
        aspect_ratio = 832 / 480
        new_width = round(height * aspect_ratio / 16) * 16
        new_width = max(64, min(2048, new_width))
        
        return gr.update(value=new_width)
    
    # 绑定事件
    i2v_width.change(
        on_width_change,
        inputs=[i2v_width, i2v_height, lock_aspect_ratio],
        outputs=[i2v_height]
    )
    
    i2v_height.change(
        on_height_change,
        inputs=[i2v_width, i2v_height, lock_aspect_ratio],
        outputs=[i2v_width]
    )
    
    return i2v_width, i2v_height, i2v_num_frames, i2v_fps, lock_aspect_ratio


# ============================================================================
# 2. 参数分类 - 共通参数
# ============================================================================

def create_common_generation_params(scheduler_choices):
    """创建共通生成参数"""
    
    with gr.Group():
        gr.Markdown("### 🎨 生成参数")
        
        with gr.Row():
            i2v_steps = gr.Slider(
                1, 100, value=30, step=1,
                label="步数 (Steps)",
                info="更多步数=更高质量，但更慢"
            )
            i2v_cfg = gr.Slider(
                0.0, 30.0, value=6.0, step=0.1,
                label="CFG Scale",
                info="提示词引导强度"
            )
        
        with gr.Row():
            i2v_shift = gr.Slider(
                0.0, 100.0, value=5.0, step=0.1,
                label="Shift",
                info="时间偏移参数"
            )
            i2v_seed = gr.Number(
                value=-1,
                label="随机种子 (Seed)",
                info="-1 表示随机"
            )
        
        i2v_scheduler = gr.Dropdown(
            choices=scheduler_choices,
            value="dpm++_sde",
            label="采样器 (Scheduler)",
            info="推荐: unipc 或 dpm++_sde"
        )
        
        i2v_denoise = gr.Slider(
            0.0, 1.0, value=1.0, step=0.01,
            label="去噪强度 (Denoise)",
            info="1.0 = 完全重新生成"
        )
    
    return i2v_steps, i2v_cfg, i2v_shift, i2v_seed, i2v_scheduler, i2v_denoise


def create_common_model_selection(available_models, available_vaes, available_t5):
    """创建共通模型选择"""
    
    with gr.Group():
        gr.Markdown("### 🧠 模型选择")
        
        i2v_model_name = gr.Dropdown(
            choices=available_models,
            value=available_models[0] if available_models else None,
            label="Diffusion 模型",
            allow_custom_value=True,
            info="主生成模型"
        )
        
        i2v_vae_name = gr.Dropdown(
            choices=available_vaes,
            value=available_vaes[0] if available_vaes else None,
            label="VAE 模型",
            allow_custom_value=True,
            info="视频编解码器"
        )
        
        i2v_t5_model = gr.Dropdown(
            choices=available_t5,
            value=available_t5[0] if available_t5 else None,
            label="T5 文本编码器",
            allow_custom_value=True,
            info="文本理解模型"
        )
    
    return i2v_model_name, i2v_vae_name, i2v_t5_model


def create_common_advanced_settings():
    """创建共通高级设置"""
    
    with gr.Accordion("⚙️ 高级设置", open=False):
        gr.Markdown("#### 性能优化")
        
        with gr.Row():
            i2v_base_precision = gr.Dropdown(
                choices=["disabled", "fp32", "bf16", "fp16", "fp16_fast", "fp8_e4m3fn", "fp8_e4m3fn_fast"],
                value="bf16",
                label="基础精度 (Base Precision)",
                info="disabled=自动检测 | bf16=推荐"
            )
            
            i2v_quantization = gr.Dropdown(
                choices=["disabled", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2", "fp4_scaled"],
                value="fp8_e4m3fn_fast",
                label="量化 (Quantization)",
                info="fp8_fast=RTX 4000+ | fp4=RTX 5090"
            )
        
        i2v_attention_mode = gr.Dropdown(
            choices=["sdpa", "flash_attn_2", "flash_attn_3", "sageattn", "sageattn_3_fp8"],
            value="sageattn",
            label="注意力模式 (Attention)",
            info="sageattn=最快 | sageattn_3_fp8=RTX 5090"
        )
        
        gr.Markdown("#### 输出格式")
        
        with gr.Row():
            output_format = gr.Dropdown(
                choices=["mp4", "gif", "webm", "frames"],
                value="mp4",
                label="输出格式",
                info="mp4=推荐"
            )
            
            fps_output = gr.Slider(
                8, 60, value=25, step=1,
                label="输出帧率",
                info="与生成帧率可以不同"
            )
    
    return i2v_base_precision, i2v_quantization, i2v_attention_mode, output_format, fps_output


# ============================================================================
# 3. 参数分类 - InfiniteTalk 专属
# ============================================================================

def create_infinitetalk_params():
    """创建 InfiniteTalk 专属参数"""
    
    with gr.Group(visible=False) as infinitetalk_settings:
        gr.Markdown("### 🎙️ InfiniteTalk 设置")
        
        audio_file = gr.Audio(
            label="音频文件 (可选)",
            type="filepath",
            info="支持 MP3, WAV, FLAC 等格式"
        )
        
        gr.Markdown("#### 窗口参数")
        
        with gr.Row():
            frame_window_size = gr.Slider(
                1, 200, value=117, step=4,
                label="帧窗口大小 (Frame Window)",
                info="每个窗口的帧数（推荐117）"
            )
            
            motion_frame = gr.Slider(
                1, 50, value=25, step=1,
                label="运动帧 (Motion Frame)",
                info="窗口重叠长度（推荐25）"
            )
        
        # Wav2Vec 模型参数
        with gr.Accordion("🎙️ Wav2Vec 音频模型设置", open=False):
            gr.Markdown("**音频处理模型配置**")
            
            wav2vec_precision = gr.Radio(
                choices=["fp16", "fp32", "bf16"],
                value="fp16",
                label="模型精度 (Precision)",
                info="fp16: 快速省显存 | fp32: 精度高 | bf16: 平衡"
            )
            
            wav2vec_device = gr.Radio(
                choices=["main_device", "offload_device", "cpu"],
                value="main_device",
                label="加载设备 (Device)",
                info="main_device: GPU | offload_device: 自动卸载 | cpu: CPU"
            )
        
        # 颜色匹配（InfiniteTalk 也支持）
        colormatch_infini = gr.Dropdown(
            choices=['disabled', 'mkl', 'hm', 'reinhard', 'mvgd', 'hm-mvgd-hm', 'hm-mkl-hm'],
            value='mkl',
            label="颜色匹配 (Color Match)",
            info="窗口间颜色匹配方法（推荐mkl）"
        )
    
    return (infinitetalk_settings, audio_file, frame_window_size, motion_frame,
            wav2vec_precision, wav2vec_device, colormatch_infini)


# ============================================================================
# 4. 参数分类 - WanAnimate 专属
# ============================================================================

def create_wananimate_params():
    """创建 WanAnimate 专属参数"""
    
    with gr.Group(visible=False) as wananimate_settings:
        gr.Markdown("### 🎭 WanAnimate 设置")
        
        gr.Markdown("#### 控制图片")
        
        with gr.Row():
            pose_images = gr.Image(
                label="姿态图片 (Pose)",
                type="pil",
                info="可选：控制角色姿态"
            )
            
            face_images = gr.Image(
                label="面部图片 (Face)",
                type="pil",
                info="可选：控制面部表情"
            )
        
        gr.Markdown("#### 控制强度")
        
        with gr.Row():
            pose_strength = gr.Slider(
                0.0, 10.0, value=1.0, step=0.01,
                label="姿态强度 (Pose Strength)",
                info="姿态控制的影响程度"
            )
            
            face_strength = gr.Slider(
                0.0, 10.0, value=1.0, step=0.01,
                label="面部强度 (Face Strength)",
                info="面部控制的影响程度"
            )
        
        animate_frame_window = gr.Slider(
            1, 200, value=77, step=1,
            label="帧窗口大小 (Frame Window)",
            info="WanAnimate 窗口大小（推荐77）"
        )
        
        colormatch_animate = gr.Dropdown(
            choices=['disabled', 'mkl', 'hm', 'reinhard', 'mvgd', 'hm-mvgd-hm', 'hm-mkl-hm'],
            value='mkl',
            label="颜色匹配 (Color Match)",
            info="窗口间颜色匹配方法（推荐mkl）"
        )
    
    return (wananimate_settings, pose_images, face_images, pose_strength,
            face_strength, animate_frame_window, colormatch_animate)


# ============================================================================
# 5. 模式切换处理
# ============================================================================

def update_mode_settings(mode):
    """
    根据选择的模式更新UI显示
    
    Args:
        mode: "InfiniteTalk" | "WanAnimate" | "Standard I2V"
    
    Returns:
        tuple: (infinitetalk_visible, wananimate_visible, recommended_params)
    """
    if mode == "InfiniteTalk":
        return (
            gr.update(visible=True),   # infinitetalk_settings
            gr.update(visible=False),  # wananimate_settings
            {
                "steps": 6,
                "cfg": 1.0,
                "scheduler": "dpm++_sde",
                "fps": 25
            }
        )
    elif mode == "WanAnimate":
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            {
                "steps": 30,
                "cfg": 6.0,
                "scheduler": "unipc",
                "fps": 30
            }
        )
    else:  # Standard I2V
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            {
                "steps": 30,
                "cfg": 6.0,
                "scheduler": "unipc",
                "fps": 25
            }
        )


# ============================================================================
# 6. 参数验证和处理
# ============================================================================

class ParameterValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_dimensions(width, height):
        """验证尺寸参数"""
        if width % 16 != 0:
            width = round(width / 16) * 16
        if height % 16 != 0:
            height = round(height / 16) * 16
        
        width = max(64, min(2048, width))
        height = max(64, min(2048, height))
        
        return width, height
    
    @staticmethod
    def validate_frames(num_frames):
        """验证帧数参数"""
        if num_frames % 4 != 0:
            num_frames = round(num_frames / 4) * 4
        
        num_frames = max(1, min(241, num_frames))
        return num_frames
    
    @staticmethod
    def get_mode_defaults(mode):
        """获取模式默认参数"""
        defaults = {
            "InfiniteTalk": {
                "steps": 6,
                "cfg": 1.0,
                "shift": 7.0,
                "scheduler": "dpm++_sde",
                "fps": 25,
                "frame_window_size": 117,
                "motion_frame": 25
            },
            "WanAnimate": {
                "steps": 30,
                "cfg": 6.0,
                "shift": 5.0,
                "scheduler": "unipc",
                "fps": 30,
                "frame_window": 77
            },
            "Standard I2V": {
                "steps": 30,
                "cfg": 6.0,
                "shift": 5.0,
                "scheduler": "unipc",
                "fps": 25
            }
        }
        
        return defaults.get(mode, defaults["Standard I2V"])


# ============================================================================
# 7. 使用示例
# ============================================================================

"""
在 wanvideo_gradio_app.py 中使用:

# 导入优化模块
from ui_optimization_patch import (
    create_aspect_ratio_controls,
    create_common_generation_params,
    create_common_model_selection,
    create_common_advanced_settings,
    create_infinitetalk_params,
    create_wananimate_params,
    update_mode_settings,
    ParameterValidator
)

# 在 create_interface() 函数中:

with gr.Tab("🖼️ Image to Video"):
    with gr.Row():
        with gr.Column(scale=1):
            # 模式选择
            i2v_mode = gr.Radio(...)
            
            # 输入图片和提示词
            input_image = gr.Image(...)
            i2v_positive_prompt = gr.Textbox(...)
            i2v_negative_prompt = gr.Textbox(...)
            
            # 共通参数 - 视频尺寸（带宽高比锁定）
            i2v_width, i2v_height, i2v_num_frames, i2v_fps, lock_aspect = create_aspect_ratio_controls()
            
            # 共通参数 - 生成参数
            i2v_steps, i2v_cfg, i2v_shift, i2v_seed, i2v_scheduler, i2v_denoise = create_common_generation_params(scheduler_choices)
            
            # 共通参数 - 模型选择
            i2v_model, i2v_vae, i2v_t5 = create_common_model_selection(available_models, available_vaes, available_t5)
            
            # 共通参数 - 高级设置
            i2v_precision, i2v_quant, i2v_attn, output_fmt, fps_out = create_common_advanced_settings()
            
            # 模式特定参数 - InfiniteTalk
            infini_group, audio, frame_win, motion, wav_prec, wav_dev, color_infini = create_infinitetalk_params()
            
            # 模式特定参数 - WanAnimate
            anim_group, pose_img, face_img, pose_str, face_str, anim_win, color_anim = create_wananimate_params()
            
            # 生成按钮
            i2v_generate_btn = gr.Button("🎬 Generate Video", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            # 输出
            i2v_video_output = gr.Video(...)
    
    # 模式切换事件
    i2v_mode.change(
        update_mode_settings,
        inputs=[i2v_mode],
        outputs=[infini_group, anim_group]
    )
"""

print("[INFO] UI Optimization Patch loaded successfully!")
print("[INFO] 功能: 宽高比锁定 | 参数分类 | 模块化组件")
