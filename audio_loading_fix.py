"""
Audio Loading Fix for InfiniteTalk
修复音频加载问题，支持多种音频格式和加载方法
"""

import torch

def load_audio_file(audio_file):
    """
    尝试使用多种方法加载音频文件
    
    Args:
        audio_file: 音频文件路径
        
    Returns:
        tuple: (waveform, sample_rate) 或 (None, None) 如果失败
    """
    waveform = None
    sample_rate = None
    
    # 方法 1: 尝试使用 torchaudio 直接加载
    try:
        import torchaudio
        waveform, sample_rate = torchaudio.load(audio_file)
        print(f"[DEBUG] Audio loaded with torchaudio: {sample_rate}Hz, shape={waveform.shape}")
        return waveform, sample_rate
    except Exception as e1:
        print(f"[WARNING] torchaudio failed: {e1}")
    
    # 方法 2: 尝试使用 soundfile
    try:
        import soundfile as sf
        waveform_np, sample_rate = sf.read(audio_file)
        waveform = torch.from_numpy(waveform_np).float()
        # 确保是 (channels, samples) 格式
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.T
        print(f"[DEBUG] Audio loaded with soundfile: {sample_rate}Hz, shape={waveform.shape}")
        return waveform, sample_rate
    except Exception as e2:
        print(f"[WARNING] soundfile failed: {e2}")
    
    # 方法 3: 尝试使用 librosa
    try:
        import librosa
        waveform_np, sample_rate = librosa.load(audio_file, sr=None, mono=False)
        waveform = torch.from_numpy(waveform_np).float()
        # 确保是 (channels, samples) 格式
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        print(f"[DEBUG] Audio loaded with librosa: {sample_rate}Hz, shape={waveform.shape}")
        return waveform, sample_rate
    except Exception as e3:
        print(f"[WARNING] librosa failed: {e3}")
    
    # 方法 4: 尝试使用 pydub + ffmpeg
    try:
        from pydub import AudioSegment
        import numpy as np
        
        # 加载音频
        audio = AudioSegment.from_file(audio_file)
        
        # 转换为 numpy 数组
        samples = np.array(audio.get_array_of_samples())
        
        # 如果是立体声，重塑为 (channels, samples)
        if audio.channels == 2:
            samples = samples.reshape((-1, 2)).T
        else:
            samples = samples.reshape((1, -1))
        
        # 归一化到 [-1, 1]
        samples = samples.astype(np.float32) / (2**15)
        
        # 转换为 torch tensor
        waveform = torch.from_numpy(samples)
        sample_rate = audio.frame_rate
        
        print(f"[DEBUG] Audio loaded with pydub: {sample_rate}Hz, shape={waveform.shape}")
        return waveform, sample_rate
    except Exception as e4:
        print(f"[WARNING] pydub failed: {e4}")
    
    print(f"[ERROR] All audio loading methods failed!")
    return None, None


# 使用示例（替换 wanvideo_gradio_app.py 中的音频加载部分）
"""
# 在 wanvideo_gradio_app.py 中找到这部分代码：
import torchaudio
waveform, sample_rate = torchaudio.load(audio_file)

# 替换为：
from audio_loading_fix import load_audio_file
waveform, sample_rate = load_audio_file(audio_file)

if waveform is None:
    print(f"[WARNING] Could not load audio file, continuing without audio...")
    audio_embeds = None
else:
    # 继续处理音频...
    audio_data = {
        "waveform": waveform,
        "sample_rate": sample_rate
    }
    # ... 后续代码 ...
"""
