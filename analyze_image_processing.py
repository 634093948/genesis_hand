#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 ComfyUI 工作流中的图片处理方式
"""

import json
import sys

workflow_path = r"E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json"

print("=" * 80)
print("分析 InfiniteTalk 工作流中的图片处理")
print("=" * 80)

with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

nodes = workflow.get('nodes', [])

# 查找图片相关的节点
image_nodes = []
for node in nodes:
    node_type = node.get('type', '')
    if any(keyword in node_type.lower() for keyword in ['image', 'load', 'resize', 'scale', 'crop']):
        image_nodes.append(node)

print(f"\n找到 {len(image_nodes)} 个图片相关节点:\n")

for node in image_nodes:
    print(f"节点 ID: {node.get('id')}")
    print(f"节点类型: {node.get('type')}")
    print(f"标题: {node.get('title', 'N/A')}")
    
    # 打印输入
    inputs = node.get('inputs', [])
    if inputs:
        print("  输入:")
        for inp in inputs:
            print(f"    - {inp.get('name')}: {inp.get('type')}")
    
    # 打印输出
    outputs = node.get('outputs', [])
    if outputs:
        print("  输出:")
        for out in outputs:
            print(f"    - {out.get('name')}: {out.get('type')}")
    
    # 打印参数
    widgets_values = node.get('widgets_values', [])
    if widgets_values:
        print(f"  参数值: {widgets_values}")
    
    print("-" * 80)

# 查找 WanVideoImageToVideoMultiTalk 节点
print("\n" + "=" * 80)
print("查找 WanVideoImageToVideoMultiTalk 节点")
print("=" * 80)

multitalk_nodes = [n for n in nodes if 'multitalk' in n.get('type', '').lower()]

for node in multitalk_nodes:
    print(f"\n节点 ID: {node.get('id')}")
    print(f"节点类型: {node.get('type')}")
    print(f"标题: {node.get('title', 'N/A')}")
    
    # 打印所有参数
    widgets_values = node.get('widgets_values', [])
    if widgets_values:
        print(f"\n参数值:")
        for i, val in enumerate(widgets_values):
            print(f"  [{i}] {val}")
    
    # 打印输入连接
    inputs = node.get('inputs', [])
    if inputs:
        print(f"\n输入连接:")
        for inp in inputs:
            link = inp.get('link')
            print(f"  - {inp.get('name')}: link={link}")

print("\n" + "=" * 80)
print("完成分析")
print("=" * 80)
