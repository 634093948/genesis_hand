import os
import folder_paths
try:
    from .videohelpersuite.nodes import VideoCombine, get_video_formats
    from .videohelpersuite.utils import imageOrLatent, floatOrInt, ContainsAll
    from .videohelpersuite.server import server
    from .videohelpersuite import latent_preview
except ImportError:
    try:
        from videohelpersuite.nodes import VideoCombine, get_video_formats
        from videohelpersuite.utils import imageOrLatent, floatOrInt, ContainsAll
        from videohelpersuite.server import server
        from videohelpersuite import latent_preview
    except ImportError:
        imageOrLatent = ("IMAGE", "LATENT")
        floatOrInt = ("FLOAT", "INT")
        
        class ContainsAll(dict):
            def __contains__(self, key):
                return True
        
        from .videohelpersuite.nodes import VideoCombine
        from .videohelpersuite.server import server
        from .videohelpersuite import latent_preview
        get_video_formats = lambda: ([], {})

class EnhancedVideoCombine(VideoCombine):
    @classmethod
    def INPUT_TYPES(s):
        base_inputs = VideoCombine.INPUT_TYPES()
        # 添加多个音频输入和音频选择器到optional中，避免破坏参数顺序
        base_inputs["optional"].update({
            "audio": ("AUDIO",),  # 保留原始音频输入（主音频）
            "audio_2": ("AUDIO",),  # 备用音频1
            "audio_3": ("AUDIO",),  # 备用音频2
            "audio_4": ("AUDIO",),  # 备用音频3
            "audio_mode": ([
                "primary_only",  # 只使用主音频
                "first_available",  # 使用第一个可用的音频
                "priority_order",  # 按优先级顺序选择
                "mix_all",  # 混合所有可用音频
                "mix_primary_backup",  # 混合主音频和备用音频
                "channel_1", "channel_2", "channel_3", "channel_4",  # 单独通道选择
                "no_audio"  # 无音频
            ], {"default": "first_available"}),
            "audio_mix_ratio": ("FLOAT", {
                "default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05,
                "display": "slider"
            })
        })
        return base_inputs

    RETURN_TYPES = ("VHS_FILENAMES", "IMAGE", "VHS_VIDEOINFO")
    RETURN_NAMES = ("Filenames", "images", "video_info")
    OUTPUT_NODE = True
    CATEGORY = "Enhanced Video"
    FUNCTION = "combine_video"

    def _get_selected_audio_source(self, audio_mode, available_channels):
        """获取选中的音频源描述"""
        if not available_channels:
            return "none"
        
        if audio_mode == "primary_only":
            return "channel_1" if 1 in available_channels else "none"
        elif audio_mode == "first_available":
            return f"channel_{available_channels[0]}" if available_channels else "none"
        elif audio_mode == "priority_order":
            sorted_channels = sorted(available_channels)
            return f"channel_{sorted_channels[0]}" if sorted_channels else "none"
        elif audio_mode.startswith("channel_"):
            channel_num = int(audio_mode.split("_")[1])
            return audio_mode if channel_num in available_channels else "none"
        elif audio_mode == "mix_all":
            return f"mixed_channels_{','.join(map(str, available_channels))}"
        elif audio_mode == "mix_primary_backup":
            if 1 in available_channels:
                backup = next((ch for ch in available_channels if ch > 1), None)
                if backup:
                    return f"mixed_channels_1,{backup}"
                return "channel_1"
            return f"channel_{available_channels[0]}" if available_channels else "none"
        elif audio_mode == "no_audio":
            return "none"
        return "unknown"
    
    def process_audio_channels(self, audio, audio_2, audio_3, audio_4, audio_mode, audio_mix_ratio):
        """处理多个音频通道，根据模式选择或混合音频"""
        import torch
        import numpy as np
        
        # 收集所有可用的音频
        audio_channels = []
        if audio is not None and audio.get('waveform') is not None:
            audio_channels.append((audio, 1))  # (音频, 通道号)
        if audio_2 is not None and audio_2.get('waveform') is not None:
            audio_channels.append((audio_2, 2))
        if audio_3 is not None and audio_3.get('waveform') is not None:
            audio_channels.append((audio_3, 3))
        if audio_4 is not None and audio_4.get('waveform') is not None:
            audio_channels.append((audio_4, 4))
        
        # 如果没有可用音频或选择了no_audio
        if not audio_channels or audio_mode == "no_audio":
            return None
        
        # 根据模式选择音频
        if audio_mode == "primary_only":
            # 只使用主音频
            for aud, ch in audio_channels:
                if ch == 1:
                    return aud
            return None
            
        elif audio_mode == "first_available":
            # 使用第一个可用的音频
            return audio_channels[0][0] if audio_channels else None
            
        elif audio_mode == "priority_order":
            # 按通道顺序选择
            audio_channels.sort(key=lambda x: x[1])
            return audio_channels[0][0] if audio_channels else None
            
        elif audio_mode.startswith("channel_"):
            # 选择特定通道
            channel_num = int(audio_mode.split("_")[1])
            for aud, ch in audio_channels:
                if ch == channel_num:
                    return aud
            return None
            
        elif audio_mode in ["mix_all", "mix_primary_backup"]:
            # 混合音频
            if len(audio_channels) < 2:
                return audio_channels[0][0] if audio_channels else None
            
            # 获取要混合的音频
            if audio_mode == "mix_primary_backup":
                # 只混合主音频和第一个备用音频
                to_mix = []
                primary = None
                backup = None
                for aud, ch in audio_channels:
                    if ch == 1:
                        primary = aud
                    elif backup is None and ch > 1:
                        backup = aud
                if primary and backup:
                    to_mix = [primary, backup]
                elif primary:
                    return primary
                elif backup:
                    return backup
                else:
                    return None
            else:  # mix_all
                to_mix = [aud for aud, _ in audio_channels]
            
            if len(to_mix) < 2:
                return to_mix[0] if to_mix else None
            
            # 执行音频混合
            base_audio = to_mix[0]
            sample_rate = base_audio['sample_rate']
            mixed_waveform = base_audio['waveform'].clone()
            
            # 混合其他音频
            for i, other_audio in enumerate(to_mix[1:], 1):
                if other_audio['sample_rate'] != sample_rate:
                    # 需要重采样（简化处理，实际应用中可能需要更复杂的重采样）
                    print(f"Warning: Audio {i+1} has different sample rate, skipping mixing")
                    continue
                
                other_waveform = other_audio['waveform']
                
                # 确保波形长度匹配
                min_length = min(mixed_waveform.shape[-1], other_waveform.shape[-1])
                mixed_waveform = mixed_waveform[..., :min_length]
                other_waveform = other_waveform[..., :min_length]
                
                # 应用混合比例
                if audio_mode == "mix_primary_backup":
                    # 主音频占比为audio_mix_ratio，备用音频占比为1-audio_mix_ratio
                    mixed_waveform = mixed_waveform * audio_mix_ratio + other_waveform * (1 - audio_mix_ratio)
                else:
                    # 平均混合所有音频
                    weight = 1.0 / len(to_mix)
                    mixed_waveform = mixed_waveform * (1 - weight) + other_waveform * weight
            
            # 归一化防止削波
            max_val = torch.abs(mixed_waveform).max()
            if max_val > 1.0:
                mixed_waveform = mixed_waveform / max_val
            
            return {
                'waveform': mixed_waveform,
                'sample_rate': sample_rate
            }
        
        # 默认返回第一个可用音频
        return audio_channels[0][0] if audio_channels else None

    def combine_video(
        self,
        frame_rate: int,
        loop_count: int,
        images=None,
        latents=None,
        filename_prefix="enhanced_video",
        format="video/h264-mp4",
        pingpong=False,
        save_output=True,
        pix_fmt="yuv420p",
        crf=19,
        preset="medium",
        save_metadata=True,
        trim_to_audio=False,
        prompt=None,
        extra_pnginfo=None,
        audio=None,
        audio_2=None,
        audio_3=None,
        audio_4=None,
        audio_mode="first_available",
        audio_mix_ratio=0.5,
        unique_id=None,
        manual_format_widgets=None,
        meta_batch=None,
        vae=None,
        **kwargs
    ):
        # 处理多通道音频
        processed_audio = self.process_audio_channels(
            audio, audio_2, audio_3, audio_4, 
            audio_mode, audio_mix_ratio
        )
        
        # 打印音频选择信息
        if processed_audio is not None:
            print(f"[Enhanced Video Combine] Audio mode: {audio_mode}")
            if audio_mode in ["mix_all", "mix_primary_backup"]:
                print(f"[Enhanced Video Combine] Mix ratio: {audio_mix_ratio}")
        else:
            print("[Enhanced Video Combine] No audio selected/available")
        
        enhanced_kwargs = {
            'pix_fmt': pix_fmt,
            'crf': crf,
            'preset': preset,
            'save_metadata': save_metadata,
            'trim_to_audio': trim_to_audio,
            **kwargs
        }
        
        # 使用处理后的音频调用父类方法
        result = super().combine_video(
            frame_rate=frame_rate,
            loop_count=loop_count,
            images=images,
            latents=latents,
            filename_prefix=filename_prefix,
            format=format,
            pingpong=pingpong,
            save_output=save_output,
            prompt=prompt,
            extra_pnginfo=extra_pnginfo,
            audio=processed_audio,  # 使用处理后的音频
            unique_id=unique_id,
            manual_format_widgets=manual_format_widgets,
            meta_batch=meta_batch,
            vae=vae,
            **enhanced_kwargs
        )

        # 直接返回原版结果，保持兼容性
        # 只在有result的情况下添加video_info
        if 'result' in result and result['result']:
            filenames, original_images = result['result']

            # 统计可用音频通道
            available_audio_channels = []
            if audio is not None and audio.get('waveform') is not None:
                available_audio_channels.append(1)
            if audio_2 is not None and audio_2.get('waveform') is not None:
                available_audio_channels.append(2)
            if audio_3 is not None and audio_3.get('waveform') is not None:
                available_audio_channels.append(3)
            if audio_4 is not None and audio_4.get('waveform') is not None:
                available_audio_channels.append(4)
            
            video_info = {
                "frame_count": len(original_images) if hasattr(original_images, '__len__') else 0,
                "frame_rate": frame_rate,
                "duration": len(original_images) / frame_rate if hasattr(original_images, '__len__') and frame_rate > 0 else 0,
                "format": format,
                "filename_prefix": filename_prefix,
                "loop_count": loop_count,
                "pingpong": pingpong,
                "has_audio": processed_audio is not None,
                "audio_mode": audio_mode,
                "audio_mix_ratio": audio_mix_ratio if audio_mode in ["mix_all", "mix_primary_backup"] else None,
                "available_audio_channels": available_audio_channels,
                "selected_audio_source": self._get_selected_audio_source(audio_mode, available_audio_channels),
                "save_output": filenames[0] if isinstance(filenames, tuple) else save_output,
                "output_files": filenames[1] if isinstance(filenames, tuple) else [],
                "pix_fmt": pix_fmt,
                "crf": crf,
                "preset": preset,
                "save_metadata": save_metadata,
                "trim_to_audio": trim_to_audio,
            }

            if hasattr(original_images, 'shape'):
                video_info.update({
                    "width": original_images.shape[2] if len(original_images.shape) > 2 else 0,
                    "height": original_images.shape[1] if len(original_images.shape) > 1 else 0,
                    "channels": original_images.shape[3] if len(original_images.shape) > 3 else 3,
                })

            # 重要：保持ui字段不变，确保动态预览能正常工作
            # 返回3个值：Filenames, images, video_info
            return {
                "ui": result.get("ui", {}),
                "result": (filenames, original_images, video_info)
            }

        # 如果没有result，直接返回原版结果
        return result

# Import audio nodes
from .audio_concat_node import NODE_CLASS_MAPPINGS as AUDIO_NODE_MAPPINGS
from .audio_concat_node import NODE_DISPLAY_NAME_MAPPINGS as AUDIO_DISPLAY_MAPPINGS

NODE_CLASS_MAPPINGS = {
    "EnhancedVideoCombine": EnhancedVideoCombine,
    **AUDIO_NODE_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EnhancedVideoCombine": "Enhanced Video Combine",
    **AUDIO_DISPLAY_MAPPINGS,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
