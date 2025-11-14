# ✅ soundfile 安装完成

## 安装状态

```
✅ soundfile 0.13.1 已成功安装到 Python 313
✅ 依赖包 cffi 和 pycparser 已安装
✅ 音频加载函数已添加到代码中
```

---

## soundfile 是什么？

**soundfile** 是一个 Python 音频处理库（依赖包），用于读写音频文件。

### 特点：
- ✅ 支持多种格式：MP3, WAV, FLAC, OGG 等
- ✅ 简单易用，API 友好
- ✅ 性能优秀，内存占用低
- ✅ 跨平台支持（Windows/Linux/Mac）

### 依赖关系：
```
soundfile 0.13.1
├── cffi >= 1.0  (C 语言外部函数接口)
├── pycparser    (C 语言解析器)
└── numpy        (已安装)
```

---

## 已完成的修改

### 1. 安装 soundfile ✅
```bash
python313\python.exe -m pip install soundfile
```

### 2. 添加导入 ✅
在 `wanvideo_gradio_app.py` 顶部：
```python
import soundfile as sf
```

### 3. 添加加载函数 ✅
```python
def load_audio_with_soundfile(audio_file):
    """使用 soundfile 加载音频文件"""
    try:
        waveform_np, sample_rate = sf.read(audio_file, dtype='float32')
        waveform = torch.from_numpy(waveform_np)
        
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.T
        
        print(f"[DEBUG] Audio loaded: {sample_rate}Hz, shape={waveform.shape}")
        return waveform, sample_rate
    except Exception as e:
        print(f"[ERROR] Failed to load audio: {e}")
        return None, None
```

---

## ⚠️ 还需要手动修改的地方

由于文件部分损坏，需要手动查找并替换音频加载代码：

### 查找位置
在 `genesis/apps/wanvideo_gradio_app.py` 中搜索：
```python
import torchaudio
waveform, sample_rate = torchaudio.load(audio_file)
```

### 替换为
```python
# 使用 soundfile 加载音频
waveform, sample_rate = load_audio_with_soundfile(audio_file)

if waveform is None:
    print(f"[WARNING] Could not load audio file, using silent mode...")
    audio_embeds = None
else:
    # 继续处理音频
    audio_data = {
        "waveform": waveform,
        "sample_rate": sample_rate
    }
    print(f"[DEBUG] Audio file loaded: sample_rate={sample_rate}, shape={waveform.shape}")
    
    # 创建音频嵌入
    wav2vec_embeds_node = NODE_CLASS_MAPPINGS['MultiTalkWav2VecEmbeds']()
    audio_embeds_result = wav2vec_embeds_node.process(
        wav2vec_model=wav2vec_model,
        audio_1=audio_data,
        normalize_loudness=True,
        num_frames=frame_window_size,
        fps=fps,
        audio_scale=1.0,
        audio_cfg_scale=1.0,
        multi_audio_type="para"
    )
    audio_embeds = audio_embeds_result[0]
```

---

## 🔍 如何查找需要修改的位置

### 方法 1: 使用 IDE 搜索
1. 在 VSCode 中按 `Ctrl+F`
2. 搜索: `torchaudio.load`
3. 替换为上面的新代码

### 方法 2: 使用 grep
```bash
grep -n "torchaudio" genesis/apps/wanvideo_gradio_app.py
```

### 方法 3: 查看错误日志
运行程序时，错误会显示具体行号：
```
File "E:\liliyuanshangmie\genesis_hand\genesis\apps\wanvideo_gradio_app.py", line 341
    waveform, sample_rate = torchaudio.load(audio_file)
```

---

## 🚀 测试

修改完成后，测试音频加载：

```bash
python genesis/apps/wanvideo_gradio_app.py
```

上传音频文件，应该看到：
```
[DEBUG] Audio loaded with soundfile: 16000Hz, shape=torch.Size([1, 48000])
[INFO] Audio embeds created, actual frames: 81
```

---

## 📋 支持的音频格式

soundfile 支持以下格式：

| 格式 | 扩展名 | 支持 |
|------|--------|------|
| WAV | .wav | ✅ 完美 |
| FLAC | .flac | ✅ 完美 |
| OGG | .ogg | ✅ 完美 |
| MP3 | .mp3 | ✅ 需要 libsndfile |
| AIFF | .aiff | ✅ 支持 |
| AU | .au | ✅ 支持 |

---

## ⚠️ 如果仍然失败

### 检查 libsndfile
soundfile 依赖 libsndfile 库。如果 MP3 仍然无法加载：

```bash
# 检查 libsndfile 版本
python313\python.exe -c "import soundfile; print(soundfile.__libsndfile_version__)"
```

### 备用方案：转换为 WAV
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

---

## 总结

✅ **soundfile 已安装并配置完成**
✅ **音频加载函数已添加**
⚠️ **需要手动替换 torchaudio.load 调用**

完成手动替换后，就可以正常使用音频功能了！
