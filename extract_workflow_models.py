#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 ComfyUI 工作流中提取所有使用的模型
"""

import json
import sys
from pathlib import Path

def extract_models_from_workflow(workflow_path):
    """从工作流 JSON 中提取所有模型引用"""
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    models = {
        'diffusion_models': set(),
        'vae': set(),
        'clip_vision': set(),
        'audio_encoders': set(),
        'wav2vec2': set(),
        'text_encoders': set(),
        'loras': set(),
        'other': set()
    }
    
    # 遍历所有节点
    for node in workflow.get('nodes', []):
        node_type = node.get('type', '')
        widgets_values = node.get('widgets_values', [])
        
        # 检查节点类型和参数
        if 'ModelLoader' in node_type or 'Load' in node_type:
            print(f"\n节点类型: {node_type}")
            print(f"  参数: {widgets_values}")
            
            # 检查是否是模型文件
            for value in widgets_values:
                if isinstance(value, str):
                    value_lower = value.lower()
                    
                    # 检查文件扩展名
                    if any(ext in value_lower for ext in ['.safetensors', '.gguf', '.bin', '.pt', '.pth', '.ckpt']):
                        # 分类模型
                        if 'vae' in value_lower:
                            models['vae'].add(value)
                        elif 'clip' in value_lower or 'vision' in value_lower:
                            models['clip_vision'].add(value)
                        elif 'wav2vec' in value_lower:
                            models['wav2vec2'].add(value)
                        elif 'whisper' in value_lower:
                            models['audio_encoders'].add(value)
                        elif 'lora' in node_type.lower():
                            models['loras'].add(value)
                        elif 't5' in value_lower or 'text' in value_lower:
                            models['text_encoders'].add(value)
                        elif 'wan' in value_lower or 'infinite' in value_lower or 'multitalk' in value_lower:
                            models['diffusion_models'].add(value)
                        else:
                            models['other'].add(value)
        
        # 特殊检查：Wav2Vec 和 Whisper 节点
        if 'wav2vec' in node_type.lower():
            print(f"\n找到 Wav2Vec 节点: {node_type}")
            print(f"  参数: {widgets_values}")
            for value in widgets_values:
                if isinstance(value, str) and value:
                    models['wav2vec2'].add(value)
        
        if 'whisper' in node_type.lower():
            print(f"\n找到 Whisper 节点: {node_type}")
            print(f"  参数: {widgets_values}")
            for value in widgets_values:
                if isinstance(value, str) and value:
                    models['audio_encoders'].add(value)
        
        if 'audio' in node_type.lower() and 'load' in node_type.lower():
            print(f"\n找到音频加载节点: {node_type}")
            print(f"  参数: {widgets_values}")
    
    return models

def main():
    workflow_path = r"E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json"
    
    print("=" * 70)
    print("从工作流中提取模型")
    print("=" * 70)
    print(f"\n工作流: {workflow_path}\n")
    
    models = extract_models_from_workflow(workflow_path)
    
    print("\n" + "=" * 70)
    print("提取的模型列表")
    print("=" * 70)
    
    for category, model_list in models.items():
        if model_list:
            print(f"\n{category}:")
            for model in sorted(model_list):
                print(f"  - {model}")
    
    # 检查是否有 Wav2Vec 或 Whisper
    print("\n" + "=" * 70)
    print("音频模型分析")
    print("=" * 70)
    
    if models['wav2vec2']:
        print("\n✅ 工作流使用 Wav2Vec 模型:")
        for model in models['wav2vec2']:
            print(f"  - {model}")
    else:
        print("\n⚠️  工作流未使用 Wav2Vec 模型")
    
    if models['audio_encoders']:
        print("\n✅ 工作流使用音频编码器（可能是 Whisper）:")
        for model in models['audio_encoders']:
            print(f"  - {model}")
    else:
        print("\n⚠️  工作流未使用音频编码器")
    
    # 保存结果
    output_file = "workflow_models.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("工作流使用的模型列表\n")
        f.write("=" * 70 + "\n\n")
        for category, model_list in models.items():
            if model_list:
                f.write(f"{category}:\n")
                for model in sorted(model_list):
                    f.write(f"  - {model}\n")
                f.write("\n")
    
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
