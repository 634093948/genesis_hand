"""
Audio Concatenate Node for Enhanced Video Combine
Author: eddy
"""

import torch
import numpy as np

class AudioConcatenate:
    """
    Concatenate multiple audio tracks in sequence
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "audio_1": ("AUDIO",),
                "audio_2": ("AUDIO",),
                "audio_3": ("AUDIO",),
                "audio_4": ("AUDIO",),
                "audio_5": ("AUDIO",),
                "audio_6": ("AUDIO",),
                "crossfade_duration": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1,
                    "display": "slider"
                }),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "concatenate_audio"
    CATEGORY = "Enhanced Video/Audio"
    
    def concatenate_audio(self, audio_1=None, audio_2=None, audio_3=None, 
                         audio_4=None, audio_5=None, audio_6=None,
                         crossfade_duration=0.0):
        """
        Concatenate audio tracks in sequence
        """
        # Collect all available audio inputs
        audio_list = []
        for i, audio in enumerate([audio_1, audio_2, audio_3, audio_4, audio_5, audio_6], 1):
            if audio is not None and audio.get('waveform') is not None:
                audio_list.append((audio, i))
        
        if len(audio_list) == 0:
            print("[Audio Concatenate] No audio inputs provided")
            return (None,)
        
        if len(audio_list) == 1:
            print(f"[Audio Concatenate] Only one audio input, returning as-is")
            return (audio_list[0][0],)
        
        print(f"[Audio Concatenate] Concatenating {len(audio_list)} audio tracks")
        
        # Get base sample rate from first audio
        base_sample_rate = audio_list[0][0]['sample_rate']
        
        # Get target channels from first audio
        base_channels = audio_list[0][0]['waveform'].shape[1] if audio_list[0][0]['waveform'].dim() == 3 else 1
        
        # Collect all waveforms
        waveforms = []
        for audio, idx in audio_list:
            waveform = audio['waveform']
            sample_rate = audio['sample_rate']
            
            # Ensure waveform is 3D [batch, channels, samples]
            if waveform.dim() == 2:
                waveform = waveform.unsqueeze(0)
            
            current_channels = waveform.shape[1]
            
            # Auto-convert channels to match
            if current_channels != base_channels:
                if current_channels == 1 and base_channels == 2:
                    # Mono to Stereo: duplicate channel
                    waveform = waveform.repeat(1, 2, 1)
                    print(f"[Audio Concatenate] Audio {idx}: Converted mono to stereo")
                elif current_channels == 2 and base_channels == 1:
                    # Stereo to Mono: average channels
                    waveform = waveform.mean(dim=1, keepdim=True)
                    print(f"[Audio Concatenate] Audio {idx}: Converted stereo to mono")
                else:
                    print(f"[Audio Concatenate] Warning: Audio {idx} has {current_channels} channels, "
                          f"expected {base_channels}")
            
            # Resample if needed
            if sample_rate != base_sample_rate:
                ratio = base_sample_rate / sample_rate
                new_length = int(waveform.shape[-1] * ratio)
                
                # Simple linear interpolation for resampling
                import torch.nn.functional as F
                waveform = F.interpolate(waveform, size=new_length, mode='linear', align_corners=False)
                
                print(f"[Audio Concatenate] Audio {idx}: Resampled from {sample_rate}Hz to {base_sample_rate}Hz")
            
            waveforms.append(waveform)
            print(f"[Audio Concatenate] Audio {idx}: shape={waveform.shape}, "
                  f"duration={waveform.shape[-1]/base_sample_rate:.2f}s")
        
        # Apply crossfade if requested
        if crossfade_duration > 0:
            waveforms = self._apply_crossfade(waveforms, base_sample_rate, crossfade_duration)
        
        # Concatenate along time axis (last dimension)
        concatenated_waveform = torch.cat(waveforms, dim=-1)
        
        total_duration = concatenated_waveform.shape[-1] / base_sample_rate
        print(f"[Audio Concatenate] Result: shape={concatenated_waveform.shape}, "
              f"total_duration={total_duration:.2f}s")
        
        return ({
            'waveform': concatenated_waveform,
            'sample_rate': base_sample_rate
        },)
    
    def _apply_crossfade(self, waveforms, sample_rate, crossfade_duration):
        """
        Apply crossfade between consecutive audio tracks
        """
        if len(waveforms) < 2:
            return waveforms
        
        crossfade_samples = int(crossfade_duration * sample_rate)
        if crossfade_samples == 0:
            return waveforms
        
        print(f"[Audio Concatenate] Applying {crossfade_duration}s crossfade "
              f"({crossfade_samples} samples)")
        
        result = []
        for i in range(len(waveforms)):
            current = waveforms[i]
            
            if i == 0:
                # First track: only fade out at the end
                if crossfade_samples < current.shape[-1]:
                    fade_out = torch.linspace(1.0, 0.0, crossfade_samples, 
                                             device=current.device, dtype=current.dtype)
                    current = current.clone()
                    current[..., -crossfade_samples:] *= fade_out
                result.append(current)
            else:
                # Middle/last tracks: fade in at start, fade out at end (except last)
                current = current.clone()
                
                # Fade in
                if crossfade_samples < current.shape[-1]:
                    fade_in = torch.linspace(0.0, 1.0, crossfade_samples,
                                            device=current.device, dtype=current.dtype)
                    current[..., :crossfade_samples] *= fade_in
                    
                    # Overlap with previous track's fade out
                    prev = result[-1]
                    overlap_start = prev.shape[-1] - crossfade_samples
                    current[..., :crossfade_samples] += prev[..., overlap_start:]
                    
                    # Remove the overlapped part from previous track
                    result[-1] = prev[..., :overlap_start]
                
                # Fade out (except for last track)
                if i < len(waveforms) - 1 and crossfade_samples < current.shape[-1]:
                    fade_out = torch.linspace(1.0, 0.0, crossfade_samples,
                                             device=current.device, dtype=current.dtype)
                    current[..., -crossfade_samples:] *= fade_out
                
                result.append(current)
        
        return result


class AudioFromFrames:
    """
    Generate audio (silence or from source) matching frame count
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "frame_rate": ("INT", {
                    "default": 25,
                    "min": 1,
                    "max": 60,
                    "step": 1
                }),
                "sample_rate": ("INT", {
                    "default": 44100,
                    "min": 8000,
                    "max": 96000,
                    "step": 100
                }),
                "channels": (["mono", "stereo"], {"default": "stereo"}),
            },
            "optional": {
                "audio": ("AUDIO",),  # Optional audio to use instead of silence
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_audio"
    CATEGORY = "Enhanced Video/Audio"
    
    def generate_audio(self, images, frame_rate, sample_rate, channels, audio=None):
        """
        Generate audio matching frame count duration
        """
        # Calculate duration from frames
        num_frames = images.shape[0]
        duration = num_frames / frame_rate
        
        print(f"[Audio From Frames] {num_frames} frames at {frame_rate}fps = {duration:.2f}s")
        
        if audio is not None and audio.get('waveform') is not None:
            # Trim or pad existing audio to match duration
            waveform = audio['waveform']
            audio_sample_rate = audio['sample_rate']
            
            target_samples = int(duration * audio_sample_rate)
            current_samples = waveform.shape[-1]
            
            if current_samples > target_samples:
                # Trim audio
                waveform = waveform[..., :target_samples]
                print(f"[Audio From Frames] Trimmed audio from {current_samples} to {target_samples} samples")
            elif current_samples < target_samples:
                # Pad with silence
                padding = torch.zeros(*waveform.shape[:-1], target_samples - current_samples)
                waveform = torch.cat([waveform, padding], dim=-1)
                print(f"[Audio From Frames] Padded audio from {current_samples} to {target_samples} samples")
            
            return ({
                'waveform': waveform,
                'sample_rate': audio_sample_rate
            },)
        else:
            # Generate silence
            num_channels = 1 if channels == "mono" else 2
            num_samples = int(duration * sample_rate)
            
            # Create silent waveform [batch, channels, samples]
            waveform = torch.zeros(1, num_channels, num_samples, dtype=torch.float32)
            
            print(f"[Audio From Frames] Generated {duration:.2f}s of silence "
                  f"({channels}, {sample_rate}Hz)")
            
            return ({
                'waveform': waveform,
                'sample_rate': sample_rate
            },)


class AudioSilence:
    """
    Generate silent audio of specified duration
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "duration": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 60.0,
                    "step": 0.1
                }),
                "sample_rate": ("INT", {
                    "default": 44100,
                    "min": 8000,
                    "max": 96000,
                    "step": 100
                }),
                "channels": (["mono", "stereo"], {"default": "stereo"}),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate_silence"
    CATEGORY = "Enhanced Video/Audio"
    
    def generate_silence(self, duration, sample_rate, channels):
        """
        Generate silent audio
        """
        num_channels = 1 if channels == "mono" else 2
        num_samples = int(duration * sample_rate)
        
        # Create silent waveform [batch, channels, samples]
        waveform = torch.zeros(1, num_channels, num_samples, dtype=torch.float32)
        
        print(f"[Audio Silence] Generated {duration}s of silence "
              f"({channels}, {sample_rate}Hz)")
        
        return ({
            'waveform': waveform,
            'sample_rate': sample_rate
        },)


class ImageConcatenate:
    """
    Concatenate multiple image sequences in order
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_6": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "concatenate_images"
    CATEGORY = "Enhanced Video/Image"
    
    def concatenate_images(self, image_1=None, image_2=None, image_3=None,
                          image_4=None, image_5=None, image_6=None):
        """
        Concatenate image sequences in order with automatic resolution matching
        """
        import torch.nn.functional as F
        
        # Collect all available image inputs
        image_list = []
        for i, images in enumerate([image_1, image_2, image_3, image_4, image_5, image_6], 1):
            if images is not None:
                image_list.append((images, i))
        
        if len(image_list) == 0:
            print("[Image Concatenate] No image inputs provided")
            raise ValueError("At least one image input is required")
        
        if len(image_list) == 1:
            print(f"[Image Concatenate] Only one image input, returning as-is")
            return (image_list[0][0],)
        
        print(f"[Image Concatenate] Concatenating {len(image_list)} image sequences")
        
        # Find the target resolution (use the first sequence's resolution)
        target_images = image_list[0][0]
        target_height = target_images.shape[1]
        target_width = target_images.shape[2]
        
        print(f"[Image Concatenate] Target resolution: {target_width}x{target_height}")
        
        # Collect and resize all images to match target resolution
        all_images = []
        total_frames = 0
        for images, idx in image_list:
            num_frames = images.shape[0]
            height = images.shape[1]
            width = images.shape[2]
            
            # Check if resize is needed
            if height != target_height or width != target_width:
                print(f"[Image Concatenate] Sequence {idx}: Resizing from {width}x{height} to {target_width}x{target_height}")
                
                # Resize: [B, H, W, C] -> [B, C, H, W] -> resize -> [B, C, H', W'] -> [B, H', W', C]
                images_transposed = images.permute(0, 3, 1, 2)  # [B, C, H, W]
                images_resized = F.interpolate(
                    images_transposed, 
                    size=(target_height, target_width),
                    mode='bilinear',
                    align_corners=False
                )
                images = images_resized.permute(0, 2, 3, 1)  # [B, H', W', C]
            
            total_frames += num_frames
            all_images.append(images)
            print(f"[Image Concatenate] Sequence {idx}: {num_frames} frames, "
                  f"final_shape={images.shape}")
        
        # Concatenate along batch dimension (first dimension)
        concatenated_images = torch.cat(all_images, dim=0)
        
        print(f"[Image Concatenate] Result: {total_frames} total frames, "
              f"shape={concatenated_images.shape}")
        
        return (concatenated_images,)


NODE_CLASS_MAPPINGS = {
    "AudioConcatenate": AudioConcatenate,
    "AudioSilence": AudioSilence,
    "AudioFromFrames": AudioFromFrames,
    "ImageConcatenate": ImageConcatenate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioConcatenate": "Audio Concatenate",
    "AudioSilence": "Audio Silence",
    "AudioFromFrames": "Audio From Frames",
    "ImageConcatenate": "Image Concatenate",
}
