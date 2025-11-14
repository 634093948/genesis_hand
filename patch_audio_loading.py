"""
音频加载补丁脚本
自动修复 wanvideo_gradio_app.py 中的音频加载问题
"""

import re

# 读取文件
file_path = "genesis/apps/wanvideo_gradio_app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换 torchaudio.load 调用
# 模式 1: import torchaudio 后的 waveform, sample_rate = torchaudio.load(audio_file)
pattern1 = r'import torchaudio\s+waveform, sample_rate = torchaudio\.load\(audio_file\)'
replacement1 = '''# 使用 soundfile 加载音频（已安装）
                        waveform, sample_rate = load_audio_with_soundfile(audio_file)
                        
                        if waveform is None:
                            print(f"[WARNING] Could not load audio file, using silent mode...")
                            audio_embeds = None
                        else'''

# 模式 2: 单独的 torchaudio.load 调用
pattern2 = r'waveform, sample_rate = torchaudio\.load\(audio_file\)'
replacement2 = '''waveform, sample_rate = load_audio_with_soundfile(audio_file)
                        
                        if waveform is None:
                            print(f"[WARNING] Could not load audio file, using silent mode...")
                            continue  # 跳过音频处理'''

# 尝试替换
modified = False

if re.search(pattern1, content):
    content = re.sub(pattern1, replacement1, content)
    modified = True
    print("✓ 替换了 pattern1: import torchaudio + load")

if re.search(pattern2, content):
    content = re.sub(pattern2, replacement2, content)
    modified = True
    print("✓ 替换了 pattern2: torchaudio.load")

# 如果没有找到模式，手动查找
if not modified:
    print("\n未找到标准模式，手动搜索 'torchaudio' ...")
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'torchaudio' in line.lower():
            print(f"第 {i+1} 行: {line.strip()}")

# 保存修改
if modified:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ 文件已更新: {file_path}")
else:
    print("\n⚠️ 未进行任何修改")
    print("\n请手动查找并替换以下代码:")
    print("\n原代码:")
    print("    import torchaudio")
    print("    waveform, sample_rate = torchaudio.load(audio_file)")
    print("\n新代码:")
    print("    waveform, sample_rate = load_audio_with_soundfile(audio_file)")
    print("    if waveform is None:")
    print("        print('[WARNING] Could not load audio, using silent mode...')")
    print("        audio_embeds = None")
    print("    else:")
    print("        # 继续处理音频...")
