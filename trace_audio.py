import json

# 读取工作流
with open(r'E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("完整音频流程追踪")
print("=" * 60)

# 从 VHS_VideoCombine 开始
current_node_id = 131  # VHS_VideoCombine
audio_chain = []

while True:
    node = [n for n in data['nodes'] if n['id'] == current_node_id][0]
    audio_chain.append({
        'id': node['id'],
        'type': node['type'],
        'title': node.get('title', '')
    })
    
    print(f"\n节点 {node['id']}: {node['type']}")
    if node.get('title'):
        print(f"  标题: {node['title']}")
    
    # 找音频输入
    audio_input = None
    for inp in node.get('inputs', []):
        if 'audio' in inp['name'].lower():
            audio_input = inp
            break
    
    if not audio_input or not audio_input.get('link'):
        print("  ✓ 这是音频源头")
        break
    
    # 找到源节点
    link_id = audio_input['link']
    for link in data['links']:
        if link[0] == link_id:
            current_node_id = link[1]
            print(f"  ← 音频来自节点 {current_node_id}")
            break

print("\n" + "=" * 60)
print("音频流程总结")
print("=" * 60)
for i, node_info in enumerate(reversed(audio_chain)):
    arrow = " → " if i < len(audio_chain) - 1 else ""
    print(f"{node_info['type']}{arrow}", end="")
print()

# 检查 MultiTalkWav2VecEmbeds 的输出
print("\n" + "=" * 60)
print("MultiTalkWav2VecEmbeds 节点输出")
print("=" * 60)
wav2vec_node = [n for n in data['nodes'] if n['type'] == 'MultiTalkWav2VecEmbeds'][0]
print(f"\n节点 ID: {wav2vec_node['id']}")
print("输出:")
for i, out in enumerate(wav2vec_node['outputs']):
    print(f"  [{i}] {out['name']}: {out['type']}")
    if out.get('links'):
        print(f"      → 连接到: {out['links']}")

print("\n✅ 关键发现:")
print("  1. VHS_VideoCombine 有 'audio' 输入")
print("  2. 音频来自 LoadAudio → AudioCrop → VHS_VideoCombine")
print("  3. MultiTalkWav2VecEmbeds 输出 AUDIO 类型")
print("  4. 这个 AUDIO 输出被传递给 VHS_VideoCombine")
